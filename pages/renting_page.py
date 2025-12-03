import streamlit as st
import pandas as pd
from datetime import date
from login import load_data
import plotly.express as px 
import plotly.graph_objects as go 

# to run predictions
from computations import run_computations_renting


# to format numbers in thousands like: 1'000 and so on
def fmt(num):
    return f"{num:,.0f}".replace(",", "'")

# Map for official Arrondissement names (used for title/caption)
arrondissement_names = {
    1: "1er Ardt - Louvre", 2: "2e Ardt - Bourse", 3: "3e Ardt - Temple", 4: "4e Ardt - Hôtel-de-Ville", 5: "5e Ardt - Panthéon",
    6: "6e Ardt - Luxembourg", 7: "7e Ardt - Palais-Bourbon", 8: "8e Ardt - Élysée", 9: "9e Ardt - Opéra", 10: "10e Ardt - Entrepôt",
    11: "11e Ardt - Popincourt", 12: "12e Ardt - Reuilly", 13: "13e Ardt - Gobelins", 14: "14e Ardt - Observatoire", 15: "15e Ardt - Vaugirard",
    16: "16e Ardt - Passy", 17: "17e Ardt - Batignolles-Monceau", 18: "18e Ardt - Buttes-Montmartre", 19: "19e Ardt - Buttes-Chaumont", 20: "20e Ardt - Ménilmontant",
}

def renting_page():

    # Load user profile if logged in
    username = st.session_state.get("username")
    all_users = load_data()
    user_profile = all_users.get(username, {}) if username else {}


    # Minimal Styling 
    st.markdown("""
        <style>
        .big-title { font-size: 36px; font-weight: 800; margin-bottom: 0.25rem; }
        .subtitle { color: #6b7280; margin-top: -0.25rem; }
        .card {
            border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px; background: #242424; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.2); color: white;
        }
        .pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#4338ca; font-size:12px; }
        </style>
    """, unsafe_allow_html=True)

    # Header 
    st.markdown('<div class="big-title">Renting Price Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Data-driven monthly renting prediction for optimal profitability </div>', unsafe_allow_html=True)
    st.divider()

    # Sidebar: Inputs 
    with st.sidebar:
        st.header("Renting details")

        city = st.selectbox("City", ["Paris", "Vienna", "Berlin", "Zurich"])
        arrondissement = st.number_input("Arrondissement",min_value=1, max_value=20,value=int(user_profile.get("arrondissement", 1)), step=1)

        default_rooms = int(user_profile.get("bathrooms", 0)) + int(user_profile.get("bedrooms", 0))
        rooms = st.number_input("Number of Rooms", min_value=1, max_value=10, value=max(1, default_rooms), step=1)
        
        furnished = st.checkbox("Is your object furnished", value = False)

        user_sidebar_data_plus_rent = {
            "Number of rooms renting": rooms,
            "arrondissement": arrondissement,
            "furnished": furnished,
        }

        # RUN PREDICTIONS
        run_computations_renting(user_sidebar_data_plus_rent)
        prediction_rent_price_user = st.session_state.get("user_renting_price_prediction", 0)
        
    # Main content (Full Width)
    
    # 1. Suggested Rent KPI (Volle Breite)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Suggested Monthly Rent")
    
    low_price_renting  = int(prediction_rent_price_user * 0.85)
    high_price_renting = int(prediction_rent_price_user * 1.15)
    
    
    kpi1, kpi2 = st.columns([1, 1])
    kpi1.metric("Predicted Monthly Rent", f"€{fmt(prediction_rent_price_user)}", delta_color="off")
    kpi2.metric("Potential Range", f"€{fmt(low_price_renting)} - €{fmt(high_price_renting)}", delta_color="off")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. Price Comparison Chart (Ersatz für die Map)
    st.markdown('<div class="card">', unsafe_allow_html=True) 
    st.subheader("Price Range")
    
    rent_data = pd.DataFrame({
        'Price (€)': [low_price_renting, prediction_rent_price_user, high_price_renting],
        'Category': ['Low End', 'Suggested Rate', 'High End']
    })

    fig_rent = px.bar(
        rent_data, 
        x='Price (€)', 
        y='Category', 
        orientation='h', 
        color='Category',
        color_discrete_map={
            'Low End': 'rgba(107, 114, 128, 0.4)', 
            'Suggested Rate': '#E57370', # App-Akzentfarbe
            'High End': 'rgba(107, 114, 128, 0.6)' 
        },
        title=f"Your Predicted Rent ({arrondissement_names.get(arrondissement, 'Paris')}) vs. Market Range"
    )

    fig_rent.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        title_font_color='white',
        height=300
    )

    st.plotly_chart(fig_rent, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


    # Footer
    st.divider()
    st.markdown('<span class="pill">Renting Prediction Tab</span>', unsafe_allow_html=True)


# allow running this file directly with `streamlit run renting_page.py`
if __name__ == "__main__":
    renting_page()