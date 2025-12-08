import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go  # WICHTIG: Hinzugefügt für den Bullet Chart
import json # Correct standard library import
from login import load_data
from computations import run_computations_airbnb, predict_all_arrondissement_prices, calculate_price_impact_kpis
import numpy as np


# to format numbers in thousands like: 1'000 and so on 
def fmt(num): 
    return f"{num:,.0f}".replace(",", "'")

def airbnb_page():
    
    # --- GeoJSON Loading: ---
    geojson_data = None
    GEOJSON_FEATURE_ID_KEY = "properties.c_arinsee"

    try:
        # After moving to the flat structure, the path is simply 'data/paris.geojson'
        geojson_path_relative = "data/paris.geojson" 
        
        with open(geojson_path_relative, "r", encoding='utf-8') as f:
            geojson_data = json.load(f)
            
    except FileNotFoundError:
        st.error(f"Error: paris.geojson not found at expected path: {geojson_path_relative}. Map cannot be rendered.")
    except json.JSONDecodeError:
        st.error("Error: Could not decode paris.geojson. Check file format.")
    except Exception as e:
        st.error(f"An unexpected error occurred during GeoJSON loading: {e}")


    # Load user profile if logged in 
    username = st.session_state.get("username")
    all_users = load_data()
    user_profile = all_users.get(username, {}) if username else {}

    
    # Profile defaults need to save default stuff in order to be able to reload them once reset button is clicked!
    

    arr_default = int(user_profile.get("arrondissement", 1))
    bed_default = int(user_profile.get("bedrooms", 1))
    bath_default = int(user_profile.get("bathrooms", 1))
    host_list_default = int(user_profile.get("host_listings_count", 0))
    host_verified_default = bool(user_profile.get("host_identity_verified", False))
    #num_rooms_default = int(user_profile.get("num_rooms", 1)) --> not needed anymore
    host_superhost_default = bool(user_profile.get("host_is_superhost", False))

    room_type_options = ["Entire home/apt", "Private room", "Shared room", "Hotel room"]
    saved_room_type = user_profile.get("room_type", "Entire home/apt")

    
    #ameities options in airbnb_page
    from computations import label_to_amenity_col

    amenities_options = list(label_to_amenity_col.keys())

    user_amenities = user_profile.get("amenities", [])
    
    # Normalize saved amenities (fixes WiFi → Wifi mismatch)
    normalized_amenities = []
    for a in user_amenities:
        if a in amenities_options:
            normalized_amenities.append(a)
        else:
            # try case-normalization
            for opt in amenities_options:
                if opt.lower() == a.lower():
                    normalized_amenities.append(opt)
                    break

    default_amenities = normalized_amenities



    # Build sidebar defaults dictionary 
    sidebar_defaults = {
        "sb_city": "Paris",
        "sb_arrondissement": arr_default,
        "sb_bedrooms": bed_default,
        "sb_bathrooms": bath_default,
        #"sb_accommodates": 2, cool but no so useful --> ask philipp if he wants to keep
        "sb_host_listings_count": host_list_default,
        "sb_host_identity_verified": host_verified_default,
        "sb_room_type": saved_room_type,
        #"sb_room_quality": 3,  cool but no so useful --> ask philipp if he wants to keep
        #"sb_min_nights": 2,  cool but no so useful --> ask philipp if he wants to keep
        #"sb_num_rooms": num_rooms_default,
        "sb_host_is_superhost": host_superhost_default,
        "sb_amenities": default_amenities,
        #"sb_instant_book": True,  cool but no so useful --> ask philipp if he wants to keep
    }

    # Handle reset request before widgets are created  --> had problems, asked ChatGPT and told me i needed this
    if st.session_state.get("sb_reset_requested", False):
        for k, v in sidebar_defaults.items(): st.session_state[k] = v
        st.session_state["sb_reset_requested"] = False

    # Initialize any missing keys (first run) 
    for k, v in sidebar_defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    
    # Minimal Styling 
    st.markdown("""
        <style>
        .big-title { font-size: 36px; font-weight: 800; margin-bottom: 0.25rem; }
        .subtitle { color: #6b7280; margin-top: -0.25rem; }
        .card {
            border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#4338ca; font-size:12px; }
        </style>
    """, unsafe_allow_html=True)

    # Header 
    st.markdown('<div class="big-title">Airbnb Price Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Data-driven pricing for optimal profitability </div>', unsafe_allow_html=True)
    st.divider()

    # Sidebar: Inputs 
    with st.sidebar:
        st.header("Listing details")

        city = st.selectbox("City", ["Paris", "Vienna", "Berlin", "Zurich"], key="sb_city")
        arrondissement = st.number_input("Arrondissement", min_value=1, max_value=20, key="sb_arrondissement")

        colA, colB = st.columns(2)
        
        with colA:
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=10, key="sb_bedrooms")
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, key="sb_bathrooms")
            #accommodates = st.number_input("Accommodates", min_value=1, max_value=16, key="sb_accommodates")
            host_is_superhost = st.checkbox("Host is Superhost", key="sb_host_is_superhost")

        with colB:
            room_type = st.selectbox("Property type", room_type_options, key="sb_room_type")
            host_listings_count = st.number_input("Host Listings Count", min_value=0, max_value=50, key="sb_host_listings_count")

            #room_quality = st.select_slider("Quality (subjective)", options=list(range(1, 6)), key="sb_room_quality")
            #min_nights = st.number_input("Minimum nights", min_value=1, max_value=60, key="sb_min_nights")
            #num_rooms = st.number_input("Number of Rooms", min_value=1, max_value=20, key="sb_num_rooms")
            host_identity_verified = st.checkbox("Host Identity Verified", key="sb_host_identity_verified")
        
        st.subheader("Amenities")
        amenities = st.multiselect("Choose amenities", amenities_options, key="sb_amenities")
        
        #instant_book = st.toggle("Instant bookable", key="sb_instant_book")

        # Reset button: to put values at user default values
        if st.button("Reset to your default values"):
            st.session_state["sb_reset_requested"] = True
            st.rerun()

        # data dict for prediction
        user_sidebar_data = {
            "host_is_superhost": host_is_superhost,
            "host_listings_count": host_listings_count,
            "host_identity_verified": host_identity_verified,
            "bathrooms": bathrooms,
            "bedrooms": bedrooms,
            "arrondissement": arrondissement,
            "room_type": room_type,
            #"num_rooms": num_rooms,
            "amenities": amenities,
        }


        # --- MODEL COMPUTATIONS ---
        run_computations_airbnb(user_sidebar_data) # Saves predicted price (per night) and cleaning cost to st.session_state
        
        # NEW: Predict price for current listing across all 20 Arrondissements for Heatmap
        try:
            df_map_prices = predict_all_arrondissement_prices(user_sidebar_data)
            st.session_state["df_map_prices"] = df_map_prices # Store DataFrame for map visualization
        except Exception as e:
            st.warning(f"Could not run all Arrondissement predictions: {e}")
            st.session_state["df_map_prices"] = None
            
        # Retrieve computed values from session state
        pred_price_per_night = st.session_state.get("user_price_prediction", 0)
        pred_cleaning_cost = st.session_state.get("user_cleaning_cost_prediction", 0)

        try:
            impact_kpis = calculate_price_impact_kpis(user_sidebar_data, pred_price_per_night)
            st.session_state["impact_kpis"] = impact_kpis
        except Exception as e:
            st.error(f"Could not calculate price impact KPIs: {e}")
            st.session_state["impact_kpis"] = None

        # --- REVENUE COMPUTATION ---
    
        # Robustly load occupancy data for the revenue calculation
        try:
            data_arrondissement_occupancy = pd.read_csv("data/occupancy_arrondissement.csv")
            # Median of the 'Occupancy in percent' column across all districts
            city_median_occupancy = data_arrondissement_occupancy["Occupancy in percent"].median() 
            st.session_state["city_median_occupancy"] = city_median_occupancy
            arrondissement_user = int(arrondissement)

            occupancy_data = data_arrondissement_occupancy.loc[data_arrondissement_occupancy["Arrondissement"] == arrondissement_user, "Occupancy in percent"]
            
            if not occupancy_data.empty:
                 occupation = occupancy_data.iloc[0]/100 # Convert percentage to decimal
            else:
                 occupation = 0.5 # Fallback if district data is missing
                 st.warning("Occupancy data missing for the selected Arrondissement. Using default 50%.")
                 
        except FileNotFoundError:
            st.error("Occupancy data file (occupancy_arrondissement.csv) not found. Using default 50%.")
            occupation = 0.5
        except Exception as e:
             st.error(f"Error reading occupancy data: {e}")
             occupation = 0.5


        prediction_monthly_revenue_user = pred_price_per_night * 30 * occupation
        number_of_monthly_cleanings = (30 * occupation) / 4.8 
        prediction_cleaning_costs_per_month_user = number_of_monthly_cleanings * pred_cleaning_cost
        prediction_net_income_user = prediction_monthly_revenue_user - prediction_cleaning_costs_per_month_user

        # Store all final revenue figures for use in the main content
        st.session_state["prediction_net_income_user"] = prediction_net_income_user
        st.session_state["prediction_monthly_revenue_user"] = prediction_monthly_revenue_user
        st.session_state["prediction_cleaning_costs_per_month_user"] = prediction_cleaning_costs_per_month_user
        st.session_state["occupation_rate"] = occupation # NEW: Store occupation for comparison chart


    # Main content of page
    tab_summary, tab_map_analysis, price_contribution_breakdown = st.tabs([
        "Prediction Summary", 
        "Location & Map", 
        "Price Contribution Breakdown"
    ])

    with tab_summary:
        
        # Zuerst die Variablen aus der Session abrufen
        prediction_net_income_user = st.session_state.get("prediction_net_income_user", 0) 
        prediction_monthly_revenue_user = st.session_state.get("prediction_monthly_revenue_user", 0)
        prediction_cleaning_costs_per_month_user = st.session_state.get("prediction_cleaning_costs_per_month_user", 0)
        
        
        # 1. Price & Breakdown
        st.markdown('<div class="card" style="background: #333; color: white;">', unsafe_allow_html=True)
        st.subheader("📈 Price per Night")
        
        low, high = int(pred_price_per_night * 0.85), int(pred_price_per_night * 1.15)
        
        col_price1, col_price2 = st.columns(2)
        col_price1.metric("Suggested nightly rate", f"€{pred_price_per_night}")
        col_price2.metric("Competitive range", f"€{low} - €{high}")

        
        range_max = high
        target_value = pred_price_per_night

        fig = go.Figure()

        # Hintergrundbalken für die gesamte Range (Low bis High)
        fig.add_trace(go.Bar(
            y=['Price'],
            x=[range_max],
            orientation='h',
            marker=dict(color='rgba(107, 114, 128, 0.2)'),
            name='Competitive Range'
        ))

        # Target Bar (For Targetvalue)
        fig.add_trace(go.Bar(
            y=['Price'],
            x=[target_value],
            orientation='h',
            marker=dict(color='#E57370'), 
            name='Suggested Rate',
            width=0.6 
        ))

        # Vertikal Line low-end-value
        fig.add_shape(type="line",
            x0=low, x1=low, y0=-0.5, y1=0.5,
            line=dict(color="darkgray", width=2, dash="dot"),
        )
        # Vertikal Line High-End-value
        fig.add_shape(type="line",
            x0=high, x1=high, y0=-0.5, y1=0.5,
            line=dict(color="darkgray", width=2, dash="dot"),
        )
        
        # Layout-tuning
        fig.update_layout(
            barmode='overlay',
            height=150,
            xaxis=dict(range=[0, range_max * 1.1], title="Price (€)"),
            yaxis=dict(showticklabels=False), 
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            plot_bgcolor='#111111', 
            paper_bgcolor='#111111',
        )

        st.plotly_chart(fig, use_container_width=True)


        
        # 2. Net Monthly Income
        st.markdown('<div class="card" style="background: #333; color: white;">', unsafe_allow_html=True)
        st.subheader("💰 Net Monthly Income")
        
        low_net_income, high_net_income = int(prediction_net_income_user * 0.85), int(prediction_net_income_user * 1.15)
        
        col_net1, col_net2 = st.columns([1.5, 2])
        col_net1.markdown(f"## €{fmt(prediction_net_income_user)}")
        col_net2.metric("Potential range", f"€{fmt(low_net_income)} - €{fmt(high_net_income)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Detaillierter Breakdown
        breakdown_data = {
            "Metric": ["Gross Revenue", "Cleaning Costs", "Net Income"],
            "Value (€)": [
                f"{fmt(prediction_monthly_revenue_user)}",
                f"-{fmt(prediction_cleaning_costs_per_month_user)}",
                f"**{fmt(prediction_net_income_user)}**"
            ]
        }
        st.table(pd.DataFrame(breakdown_data))
        
        st.caption(f"*Estimated monthly cleaning cost per cleaning: €{pred_cleaning_cost}")
        
        st.markdown('</div>', unsafe_allow_html=True)


    with tab_map_analysis:
        
        # Retrieve computed data from session state
        map_price_df = st.session_state.get("df_map_prices")
        arrondissement_user_num = int(arrondissement)
        occupation = st.session_state.get("occupation_rate", 0.5)
        city = st.session_state.get("sb_city", "Paris")
        coords = {"Paris": (48.8566, 2.3522), "Vienna": (48.2082, 16.3738), "Berlin": (52.5200, 13.4050), "Zurich": (47.3769, 8.5417)}[city]
        
        # Mapping Arrondissement number to the 5-digit INSEE Code (e.g., 3 -> 75103)
        insee_map = {1: 75101, 2: 75102, 3: 75103, 4: 75104, 5: 75105, 6: 75106, 7: 75107, 8: 75108, 9: 75109, 10: 75110, 11: 75111, 12: 75112, 13: 75113, 14: 75114, 15: 75115, 16: 75116, 17: 75117, 18: 75118, 19: 75119, 20: 75120}
        arrondissement_insee_code = str(insee_map.get(arrondissement_user_num, 75101))


        st.markdown('<div class="card" style="background: #242424; color: white;">', unsafe_allow_html=True)
        st.subheader("Map & Price Analysis")


        
        if geojson_data and map_price_df is not None:
            
            # --- PLOTLY CHOROPLETH MAP ---
            
            
            # 1. Main Heatmap: Shows the prices of all 20 Arrondissements
            fig_map = px.choropleth_mapbox(
                map_price_df, 
                geojson=geojson_data, 
                locations='Arrondissement_Code', 
                featureidkey=GEOJSON_FEATURE_ID_KEY, 
                color='Avg_Price_Apt',
                color_continuous_scale="Reds", 
                range_color=(map_price_df['Avg_Price_Apt'].min() * 0.9, map_price_df['Avg_Price_Apt'].max() * 1.1),
                mapbox_style="carto-positron", 
                zoom=10.5, 
                center={"lat": coords[0], "lon": coords[1]},
                opacity=0.8,
                
                # --- NEUE HOVER-KONFIGURATION ---
                hover_name='Arrondissement_Name', # Zeigt den Namen des Bezirks als Titel
                hover_data={
                    'Arrondissement_Code': False,      # GeoJSON-Code ausblenden
                    'Arrondissement_Name': False,      # Name wird bereits als Titel verwendet
                    'Arrondissement_Number': True,     # NEU: Zeige die einfache Arrondissement-Nummer
                    'Avg_Price_Apt': ':.0f€'           # Zeige den Preis als ganze Euro-Zahl
                }
            )
            
            
            # 2. Highlighting the selected Arrondissement (with a white border)
            target_df = map_price_df[map_price_df['Arrondissement_Code'] == arrondissement_insee_code]
            
            if not target_df.empty:
                 # Add a second trace (layer) only for the target Arrondissement
                 fig_map.add_trace(px.choropleth_mapbox(
                    target_df, 
                    geojson=geojson_data, 
                    locations='Arrondissement_Code',
                    featureidkey=GEOJSON_FEATURE_ID_KEY, 
                    color_discrete_sequence=['#E57370'], 
                    mapbox_style="carto-positron",
                    zoom=10.5, center={"lat": coords[0], "lon": coords[1]},
                    opacity=0.01, # Almost transparent fill
                 ).data[0])
                 
                 # Set the thick white border (Correction: Use marker.line for Choroplethmapbox)
                 fig_map.data[-1].marker.line.width = 3
                 fig_map.data[-1].marker.line.color = 'white'

            
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
            fig_map.update_geos(fitbounds="locations", visible=False)
            
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(f"The map displays the **predicted nightly rate for your listing type** in every Arrondissement, highlighting your selected Arrondissement **{arrondissement}**.")
            
        else:
            st.warning("Cannot display interactive heatmap. Check GeoJSON file and price data.")
            map_df = pd.DataFrame([{"lat": coords[0], "lon": coords[1]}])
            st.map(map_df, zoom=11)
            
        st.markdown('</div>', unsafe_allow_html=True)


        
        # --- ANPASSUNG START: Neighborhood Performance Section ---

        # 1. Start des Card-Containers für Neighborhood Performance (Dunkelgrau/Schwarz)
        st.markdown('<div class="card" style="background: #242424; color: white;">', unsafe_allow_html=True) 
        st.subheader("Neighborhood Performance")
        
        # 2. Occupancy Rate & Comparison
        # NEU: Angepasste Info-Box mit Marge (margin-bottom: 20px)
        accent_color = "#E57370" 
        background_color = "#331818" 

        st.markdown(
            f"""
            <div style="
                background-color: {background_color}; 
                color: {accent_color}; 
                padding: 10px; 
                border-radius: 5px; 
                border: 1px solid {background_color};
                font-size: 16px;
                margin-bottom: 20px; /* HIER IST DER NEUE ABSTAND */
            ">
                The calculated occupancy rate for Arrondissement <strong>{arrondissement}</strong> is <strong>{occupation * 100:.1f}%</strong> (used for income prediction).
            </div>
            """,
            unsafe_allow_html=True
        )
        
        city_median_occupancy = st.session_state.get("city_median_occupancy", 65) #Default 65
        
        comparison_df = pd.DataFrame({
            'Category': ['Your Arrondissement', 'City Median'],
            'Occupancy (%)': [occupation * 100, city_median_occupancy]
        })
        
        fig_occupancy = px.bar(
            comparison_df, 
            x='Category', 
            y='Occupancy (%)', 
            color='Category',
            color_discrete_map={'Your Arrondissement': '#E57370', 'City Median': '#808080'}, 
            text='Occupancy (%)',
            title='Occupancy Rate vs. City Median'
        )
        
        # Layout-Anpassungen für Transparenz und Kontrast
        fig_occupancy.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_occupancy.update_layout(
            showlegend=False, 
            plot_bgcolor='rgba(0, 0, 0, 0)',        
            paper_bgcolor='rgba(0, 0, 0, 0)',       
            font=dict(color='white'),
            title_font_color='white',
            height=500
        )
        
        st.plotly_chart(fig_occupancy, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)
       


    with price_contribution_breakdown:
        st.markdown('<div class="card" style="background: #242424; color: white;">', unsafe_allow_html=True)
        st.subheader("Key Price Drivers")
        
        impact_kpis = st.session_state.get("impact_kpis")
        current_predicted_price = pred_price_per_night 
        
        if impact_kpis:
            
            baseline_price = impact_kpis["baseline_price"]
            quality_impact = impact_kpis["quality_impact"]
            location_impact = impact_kpis["location_impact"]

            # --- WASSERFALL DATENSTRUKTUR FÜR go.Waterfall ---
            # 1. Baseline Price (Startwert)
            # 2. Quality Impact (Delta)
            # 3. Location Impact (Delta)
            # 4. Final Price (Endwert)
            
            data_waterfall = {
                'x': [
                    '1. Baseline Price', 
                    '2. Quality Premium', 
                    '3. Location Impact', 
                    'Final Price'
                ],
                'y': [
                    baseline_price,             # Absolute Startposition
                    quality_impact,             # Delta: Hinzugefügt durch Features
                    location_impact,            # Delta: Hinzugefügt/Subtrahiert durch Lage
                    current_predicted_price     # Absolute Endposition
                ],
                'measure': [
                    'absolute', 
                    'relative', 
                    'relative', 
                    'total'
                ],
                # Farben für positive und negative Beiträge anpassen (Rotakzente)
                'increasing': {"marker":{"color": "#E57370"}}, 
                'decreasing': {"marker":{"color": "#C70039"}}, 
                'totals': {"marker":{"color": "#808080"}}, # Grau für Start/Ende
            }
            
            # --- PLOTLY WASSERFALL CHART (go.Waterfall) ---
            
            fig_drivers = go.Figure(go.Waterfall(
                name = "Price Breakdown", 
                orientation = "v", # Vertikaler Wasserfall
                x = data_waterfall['x'],
                y = data_waterfall['y'],
                measure = data_waterfall['measure'],
                increasing = data_waterfall['increasing'],
                decreasing = data_waterfall['decreasing'],
                totals = data_waterfall['totals'],
                connector = {"line": {"color": "#808080"}},
                textposition = "outside",
                text = [f"{v}€" for v in data_waterfall['y']], # Zeigt die €-Werte über den Balken
            ))

            # --- Layout Anpassungen für Dunkles/Minimales Design ---
            fig_drivers.update_layout(
                title="Price Contribution Breakdown",
                xaxis_title="",
                yaxis_title="Price (€)",
                showlegend=False,
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                font=dict(color='white'),
                title_font_color='white',
                height=550 # Erhöht die Höhe für den vertikalen Plot
            )
            
            st.plotly_chart(fig_drivers, use_container_width=True)
            
            st.markdown("---")
            
            #Summary Text
            st.markdown(f"""
            <h5 style='color: #E57370;'>Summary of Price Impact:</h5>
            <ul style='color: white;'>
                <li>Your chosen <b>Features and Quality</b> add a premium of: <b>€{fmt(quality_impact)}</b></li>
                <li>Your <b>Arrondissement Location</b> adds/subtracts: <b>€{fmt(abs(location_impact))}</b> (vs. median location)</li>
                <li>The final predicted price is <b>€{fmt(current_predicted_price)}</b>.</li>
            </ul>
            """, unsafe_allow_html=True)

        else:
            st.warning("Feature Impact data could not be loaded. Please check model execution.")
        
        st.markdown('</div>', unsafe_allow_html=True)
