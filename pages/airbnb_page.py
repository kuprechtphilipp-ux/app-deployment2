import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from login import load_data
from computations import (
    label_to_amenity_col,
    run_computations_airbnb,
    predict_all_arrondissement_prices,
    calculate_price_impact_kpis,
)
import numpy as np


# Format numbers: 1000 → 1'000
def fmt(num):
    return f"{num:,.0f}".replace(",", "'")


def airbnb_page():

    # ------------------------------------------------------------
    # Load GeoJSON
    # ------------------------------------------------------------
    geojson_data = None
    GEOJSON_FEATURE_ID_KEY = "properties.c_arinsee"

    try:
        with open("data/paris.geojson", "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
    except:
        st.error("GeoJSON file missing or invalid. Map cannot be displayed.")

    # ------------------------------------------------------------
    # Load current user profile
    # ------------------------------------------------------------
    username = st.session_state.get("username")
    all_users = load_data()
    user_profile = all_users.get(username, {}) if username else {}

    # ------------------------------------------------------------
    # Extract user defaults
    # ------------------------------------------------------------
    arr_default = int(user_profile.get("arrondissement", 1))
    bed_default = int(user_profile.get("bedrooms", 1))
    bath_default = int(user_profile.get("bathrooms", 1))
    host_list_default = int(user_profile.get("host_listings_count", 0))
    host_verified_default = bool(user_profile.get("host_identity_verified", False))
    host_superhost_default = bool(user_profile.get("host_is_superhost", False))

    room_type_options = [
        "Entire home/apt",
        "Private room",
        "Shared room",
        "Hotel room",
    ]
    saved_room_type = user_profile.get("room_type", "Entire home/apt")

    # ------------------------------------------------------------
    # Amenity Handling — critical for preventing Streamlit errors
    # ------------------------------------------------------------
    amenities_options = list(label_to_amenity_col.keys())

    user_amenities = user_profile.get("amenities", [])

    normalized_amenities = []
    for a in user_amenities:
        # Direct match
        if a in amenities_options:
            normalized_amenities.append(a)
        else:
            # Case-insensitive fallback match
            match = next((opt for opt in amenities_options if opt.lower() == a.lower()), None)
            if match:
                normalized_amenities.append(match)

    # Final safe list
    default_amenities = [a for a in normalized_amenities if a in amenities_options]

    # ------------------------------------------------------------
    # Sidebar defaults (session-state init)
    # ------------------------------------------------------------
    sidebar_defaults = {
        "sb_city": "Paris",
        "sb_arrondissement": arr_default,
        "sb_bedrooms": bed_default,
        "sb_bathrooms": bath_default,
        "sb_host_listings_count": host_list_default,
        "sb_host_identity_verified": host_verified_default,
        "sb_room_type": saved_room_type,
        "sb_host_is_superhost": host_superhost_default,
        "sb_amenities": default_amenities,
    }

    # Reset button was clicked → restore defaults
    if st.session_state.get("sb_reset_requested", False):
        for k, v in sidebar_defaults.items():
            st.session_state[k] = v
        st.session_state["sb_reset_requested"] = False

    # Initialize missing session state entries
    for k, v in sidebar_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Clean amenities every time → avoids invalid defaults after model or UI changes
    st.session_state["sb_amenities"] = [
        a for a in st.session_state["sb_amenities"] if a in amenities_options
    ]

    # ------------------------------------------------------------
    # UI Styling
    # ------------------------------------------------------------
    st.markdown("""
        <style>
        .big-title { font-size: 36px; font-weight: 800; margin-bottom: 0.25rem; }
        .subtitle { color: #6b7280; margin-top: -0.25rem; }
        .card {
            border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        </style>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Page Header
    # ------------------------------------------------------------
    st.markdown('<div class="big-title">Airbnb Price Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Data-driven pricing for optimal profitability</div>', unsafe_allow_html=True)
    st.divider()

    # ------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------
    with st.sidebar:
        st.header("Listing details")

        city = st.selectbox("City", ["Paris", "Vienna", "Berlin", "Zurich"], key="sb_city")
        arrondissement = st.number_input("Arrondissement", min_value=1, max_value=20, key="sb_arrondissement")

        colA, colB = st.columns(2)

        with colA:
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, key="sb_bedrooms")
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, key="sb_bathrooms")
            host_is_superhost = st.checkbox("Host is Superhost", key="sb_host_is_superhost")

        with colB:
            room_type = st.selectbox("Property type", room_type_options, key="sb_room_type")
            host_listings_count = st.number_input("Host Listings Count", min_value=0, max_value=50, key="sb_host_listings_count")
            host_identity_verified = st.checkbox("Host Identity Verified", key="sb_host_identity_verified")

        st.subheader("Amenities")
        amenities = st.multiselect("Choose amenities", amenities_options, key="sb_amenities")

        # Reset button
        if st.button("Reset to your default values"):
            st.session_state["sb_reset_requested"] = True
            st.rerun()

        # Prediction input dict
        user_sidebar_data = {
            "host_is_superhost": host_is_superhost,
            "host_listings_count": host_listings_count,
            "host_identity_verified": host_identity_verified,
            "bathrooms": bathrooms,
            "bedrooms": bedrooms,
            "arrondissement": arrondissement,
            "room_type": room_type,
            "amenities": amenities,
        }

        # Run prediction models
        run_computations_airbnb(user_sidebar_data)

        try:
            st.session_state["df_map_prices"] = predict_all_arrondissement_prices(user_sidebar_data)
        except:
            st.session_state["df_map_prices"] = None

        pred_price = st.session_state.get("user_price_prediction", 0)
        pred_cleaning = st.session_state.get("user_cleaning_cost_prediction", 0)

        try:
            st.session_state["impact_kpis"] = calculate_price_impact_kpis(user_sidebar_data, pred_price)
        except:
            st.session_state["impact_kpis"] = None

        # Revenue calc
        try:
            occ_df = pd.read_csv("data/occupancy_arrondissement.csv")
            city_median = occ_df["Occupancy in percent"].median()
            st.session_state["city_median_occupancy"] = city_median
            occ = occ_df.loc[occ_df["Arrondissement"] == int(arrondissement), "Occupancy in percent"]
            occupation = occ.iloc[0] / 100 if not occ.empty else 0.5
        except:
            occupation = 0.5

        monthly_rev = pred_price * 30 * occupation
        monthly_clean = (30 * occupation) / 4.8 * pred_cleaning
        net_income = monthly_rev - monthly_clean

        st.session_state["prediction_monthly_revenue_user"] = monthly_rev
        st.session_state["prediction_cleaning_costs_per_month_user"] = monthly_clean
        st.session_state["prediction_net_income_user"] = net_income
        st.session_state["occupation_rate"] = occupation

    # ------------------------------------------------------------
    # TABS: Summary / Map / Price Breakdown
    # ------------------------------------------------------------
    tab_summary, tab_map, tab_contrib = st.tabs([
        "Prediction Summary",
        "Location & Map",
        "Price Contribution Breakdown",
    ])

    # ------------------------------------------------------------
    # TAB 1 — SUMMARY
    # ------------------------------------------------------------
    with tab_summary:

        pred_revenue = st.session_state["prediction_monthly_revenue_user"]
        pred_clean_month = st.session_state["prediction_cleaning_costs_per_month_user"]
        pred_net = st.session_state["prediction_net_income_user"]

        st.markdown('<div class="card" style="background:#333; color:white;">', unsafe_allow_html=True)
        st.subheader("📈 Price per Night")

        low, high = int(pred_price * 0.85), int(pred_price * 1.15)

        colA, colB = st.columns(2)
        colA.metric("Suggested nightly rate", f"€{fmt(pred_price)}")
        colB.metric("Competitive range", f"€{fmt(low)} - €{fmt(high)}")

        # Bullet Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(y=["Price"], x=[high], orientation="h",
                             marker=dict(color="rgba(107,114,128,0.2)")))
        fig.add_trace(go.Bar(y=["Price"], x=[pred_price], orientation="h",
                             marker=dict(color="#E57370"), width=0.6))

        fig.update_layout(
            height=150,
            xaxis=dict(range=[0, high * 1.1]),
            showlegend=False,
            plot_bgcolor="#111",
            paper_bgcolor="#111",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Net Income Block
        st.subheader("💰 Net Monthly Income")
        low_net, high_net = int(pred_net * 0.85), int(pred_net * 1.15)

        col1, col2 = st.columns([1.5, 2])
        col1.markdown(f"## €{fmt(pred_net)}")
        col2.metric("Potential range", f"€{fmt(low_net)} – €{fmt(high_net)}")

        st.table(pd.DataFrame({
            "Metric": ["Gross Revenue", "Cleaning Costs", "Net Income"],
            "Value (€)": [fmt(pred_revenue), f"-{fmt(pred_clean_month)}", fmt(pred_net)]
        }))

        st.caption(f"*Estimated cleaning cost per cleaning: €{pred_cleaning}")

    # ------------------------------------------------------------
    # TAB 2 — MAP
    # ------------------------------------------------------------
    with tab_map:

        map_price_df = st.session_state.get("df_map_prices")
        occupation = st.session_state["occupation_rate"]

        st.markdown('<div class="card" style="background:#242424; color:white;">', unsafe_allow_html=True)
        st.subheader("Map & Price Analysis")

        if geojson_data and map_price_df is not None:

            city = st.session_state["sb_city"]
            coords = {
                "Paris": (48.8566, 2.3522),
                "Vienna": (48.2082, 16.3738),
                "Berlin": (52.5200, 13.4050),
                "Zurich": (47.3769, 8.5417),
            }[city]

            insee_map = {
                n: 75100 + n for n in range(1, 21)
            }
            arr_code = str(insee_map.get(int(arrondissement), 75101))

            fig_map = px.choropleth_mapbox(
                map_price_df,
                geojson=geojson_data,
                locations="Arrondissement_Code",
                featureidkey=GEOJSON_FEATURE_ID_KEY,
                color="Avg_Price_Apt",
                color_continuous_scale="Reds",
                mapbox_style="carto-positron",
                zoom=10.5,
                center={"lat": coords[0], "lon": coords[1]},
                opacity=0.8,
            )

            # highlight selected arrondissement
            highlight_df = map_price_df[map_price_df["Arrondissement_Code"] == arr_code]
            if not highlight_df.empty:
                h = px.choropleth_mapbox(
                    highlight_df,
                    geojson=geojson_data,
                    locations="Arrondissement_Code",
                    featureidkey=GEOJSON_FEATURE_ID_KEY,
                    color_discrete_sequence=["#E57370"],
                    opacity=0.01,
                )
                fig_map.add_trace(h.data[0])
                fig_map.data[-1].marker.line.width = 3
                fig_map.data[-1].marker.line.color = "white"

            st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # TAB 3 — CONTRIBUTION BREAKDOWN
    # ------------------------------------------------------------
    with tab_contrib:
        st.markdown('<div class="card" style="background:#242424; color:white;">', unsafe_allow_html=True)
        st.subheader("Key Price Drivers")

        impact = st.session_state.get("impact_kpis")

        if impact:
            baseline = impact["baseline_price"]
            qual = impact["quality_impact"]
            loc = impact["location_impact"]

            fig_w = go.Figure(go.Waterfall(
                x=["Baseline", "Quality", "Location", "Final"],
                y=[baseline, qual, loc, pred_price],
                measure=["absolute", "relative", "relative", "total"],
                increasing={"marker": {"color": "#E57370"}},
                decreasing={"marker": {"color": "#C70039"}},
                totals={"marker": {"color": "#808080"}},
                text=[f"{v}€" for v in [baseline, qual, loc, pred_price]],
                textposition="outside",
            ))

            fig_w.update_layout(
                title="Price Contribution Breakdown",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                height=550,
            )

            st.plotly_chart(fig_w, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
