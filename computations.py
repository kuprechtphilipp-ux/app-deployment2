import pandas as pd
import streamlit as st
import pickle
import numpy as np

# script to run all the computations - needed to then display price, profit, etc

model_airbnb_price = pickle.load(open("ml_models/predict_airbnb_price.sav", "rb"))
model_cleaning_costs = pickle.load(open("ml_models/predict_cost_of_cleaning.sav", "rb"))
model_renting_price = pickle.load(open("ml_models/predict_renting_price.sav", "rb"))



# (NEW) Load model feature columns dynamically
airbnb_features = list(model_airbnb_price.feature_names_in_)


rent_features = [
    "Nombre de pièces principales",
    "Arrondissement_10e",
    "Arrondissement_11e",
    "Arrondissement_12e",
    "Arrondissement_13e",
    "Arrondissement_14e",
    "Arrondissement_15e",
    "Arrondissement_16e",
    "Arrondissement_17e",
    "Arrondissement_18e",
    "Arrondissement_19e",
    "Arrondissement_1er",
    "Arrondissement_20e",
    "Arrondissement_2e",
    "Arrondissement_3e",
    "Arrondissement_4e",
    "Arrondissement_5e",
    "Arrondissement_6e",
    "Arrondissement_7e",
    "Arrondissement_8e",
    "Arrondissement_9e",
    "Type de locationom_meublé",
    "Type de locationom_non meublé"
]


#Cleaning the columns names for better UX
def clean_amenity_name(col):
    # Convert model column name to a clean user-friendly label
    x = col.replace("amenity__", "").rstrip("_")
    x = x.replace("_", " ")
    x = x.replace("u2013", "–")
    return x.strip().title()

def build_amenity_maps():
    amenity_cols = [c for c in airbnb_features if c.startswith("amenity__")]
    label_to_col = {clean_amenity_name(c): c for c in amenity_cols}
    col_to_label = {c: clean_amenity_name(c) for c in amenity_cols}
    return label_to_col, col_to_label

label_to_amenity_col, amenity_col_to_label = build_amenity_maps()




def build_airbnb_feature_df(user_profile: dict) -> pd.DataFrame:
    
    # base fields
    host_is_superhost = int(bool(user_profile.get("host_is_superhost", False)))
    host_listings_count = int(user_profile.get("host_listings_count", 0))
    host_identity_verified = int(bool(user_profile.get("host_identity_verified", False)))
    bathrooms_text = int(user_profile.get("bathrooms", 1))
    bedrooms = int(user_profile.get("bedrooms", 1))

    # arrondissement one-hot
    arr_num = int(user_profile.get("arrondissement", 1))
    arr_map = {
        1: "Arrondissement_1er",
        2: "Arrondissement_2e",
        3: "Arrondissement_3e",
        4: "Arrondissement_4e",
        5: "Arrondissement_5e",
        6: "Arrondissement_6e",
        7: "Arrondissement_7e",
        8: "Arrondissement_8e",
        9: "Arrondissement_9e",
        10: "Arrondissement_10e",
        11: "Arrondissement_11e",
        12: "Arrondissement_12e",
        13: "Arrondissement_13e",
        14: "Arrondissement_14e",
        15: "Arrondissement_15e",
        16: "Arrondissement_16e",
        17: "Arrondissement_17e",
        18: "Arrondissement_18e",
        19: "Arrondissement_19e",
        20: "Arrondissement_20e",
    }

    # room type one-hot
    room_type = user_profile.get("room_type", "Entire home/apt")
    room_categories = ["Entire home/apt", "Hotel room", "Private room", "Shared room"]

    # amenities (still needed?)
    amenities = user_profile.get("amenities", []) or []

    # start with all zeros
    feat = {name: 0 for name in airbnb_features}

    # amenities dynamic one-hot
    for label in amenities:
        model_col = label_to_amenity_col.get(label)
        if model_col in feat:
            feat[model_col] = 1



    # simple numeric fields
    feat["host_is_superhost"] = host_is_superhost
    feat["host_listings_count"] = host_listings_count
    feat["host_identity_verified"] = host_identity_verified
    feat["bathrooms_text"] = bathrooms_text
    feat["bedrooms"] = bedrooms

    # arrondissement one-hot
    arr_col = arr_map.get(arr_num)
    if arr_col in feat:
        feat[arr_col] = 1

    # room type one-hot
    for r in room_categories:
        col = f"room_{r}"
        if col in feat:
            feat[col] = int(room_type == r)

    # amenities dynamic one-hot
    for label in amenities:
        model_col = label_to_amenity_col.get(label)
        if model_col in feat:
            feat[model_col] = 1


    # build DataFrame in the exact column order to make sure it works for the model
    row = [[feat[col] for col in airbnb_features]]
    df_features_airbnb = pd.DataFrame(row, columns=airbnb_features)
    
    # debug: everytime i change something a dataset gets created and overwritten
    df_features_airbnb.to_csv("data/user_dataset_airbnb.csv", index=False)
    
    return df_features_airbnb


# function the builds df for renting computation

def build_renting_feature_df(user_profile: dict) -> pd.DataFrame:

    feat = {name: 0 for name in rent_features}

    # One-hot arrondissement
    arr_num = int(user_profile.get("arrondissement", 1))

    arr_map = {
        1:  "Arrondissement_1er",
        2:  "Arrondissement_2e",
        3:  "Arrondissement_3e",
        4:  "Arrondissement_4e",
        5:  "Arrondissement_5e",
        6:  "Arrondissement_6e",
        7:  "Arrondissement_7e",
        8:  "Arrondissement_8e",
        9:  "Arrondissement_9e",
        10: "Arrondissement_10e",
        11: "Arrondissement_11e",
        12: "Arrondissement_12e",
        13: "Arrondissement_13e",
        14: "Arrondissement_14e",
        15: "Arrondissement_15e",
        16: "Arrondissement_16e",
        17: "Arrondissement_17e",
        18: "Arrondissement_18e",
        19: "Arrondissement_19e",
        20: "Arrondissement_20e",
    }

    arr_col = arr_map.get(arr_num)
    if arr_col in feat:
        feat[arr_col] = 1

    # Number of rooms
    feat["Nombre de pièces principales"] = user_profile.get("Number of rooms renting")

    # Renting type one-hot
    user_will_rent = user_profile.get("rent", False)
    user_furnished = bool(user_profile.get("furnished", False))

    #if user_will_rent: 
    if user_furnished:
        feat["Type de locationom_meublé"] = 1
        feat["Type de locationom_non meublé"] = 0  
        # Unfurnished
    else:
        feat["Type de locationom_meublé"] = 0
        feat["Type de locationom_non meublé"] = 1
    
    # if he doesn't rent set everything to 0
    #else:
        #feat["Type de locationom_meublé"] = 0
        #feat["Type de locationom_non meublé"] = 0
           
            
    row = [[feat[col] for col in rent_features]]
    df_features_renting = pd.DataFrame(row, columns=rent_features)
    
    # debug: everytime i change something a dataset gets created and overwritten
    df_features_renting.to_csv("data/user_dataset_renting.csv",  encoding="utf-8-sig", index=False)

    return df_features_renting


# run computations
def run_computations_airbnb(user_data: dict):

    # build df used for price prediction and so on
    df_airbnb = build_airbnb_feature_df(user_data)

    ###########################
    # PRICE PREDICTION PER NIGHT
    ###########################
    
    # prediction is in log --> transform back
    user_price_prediction_log = model_airbnb_price.predict(df_airbnb)
    
    # get numeric value, because it is saved in array
    value_price_prediction_log = float(user_price_prediction_log[0])       
    value_price_prediction_log_rounded = round(value_price_prediction_log, 4)   # keep enough precision
    user_price_prediction = np.expm1(value_price_prediction_log_rounded)

    # save final value as a whole number
    st.session_state["user_price_prediction"] = int(user_price_prediction)
    
    ###########################
    # CLEANING COST PRED
    ###########################
    
    # need to format dataset in correct way for prediction!
    df_cleaning_costs = df_airbnb[['bedrooms', 'bathrooms_text']].copy()
    df_cleaning_costs.columns = ['Bedroom', 'Bathroom']

    # prediction is in log --> transform back
    user_cleaning_cost_pred = model_cleaning_costs.predict(df_cleaning_costs)
    
    # get numeric value, because it is saved in array
    value_cleaning_cost_prediction = float(user_cleaning_cost_pred[0])       
    
    # save final value as a whole number
    st.session_state["user_cleaning_cost_prediction"] = int(value_cleaning_cost_prediction)
    
    
    
def run_computations_renting(user_data: dict):
    ###########################
    # RENTING COST PRED
    ###########################
    
    df_renting = build_renting_feature_df(user_data)
    
    #predict renting price
    
    user_renting_price_pred = model_renting_price.predict(df_renting)
    
    value_pred_renting_price = float(user_renting_price_pred[0]) 
    
    st.session_state["user_renting_price_prediction"] = int(value_pred_renting_price)
    #print("DEBUG: ", value_pred_renting_price)



# NEUE FUNKTION IN computations.py

# Map for generating the official 5-digit INSEE code (used for GeoJSON matching)
insee_map = {
    1: 75101, 2: 75102, 3: 75103, 4: 75104, 5: 75105,
    6: 75106, 7: 75107, 8: 75108, 9: 75109, 10: 75110,
    11: 75111, 12: 75112, 13: 75113, 14: 75114, 15: 75115,
    16: 75116, 17: 75117, 18: 75118, 19: 75119, 20: 75120,
}

# Map for official Arrondissement names (for user display/hover text)
arrondissement_names = {
    1: "1er Ardt - Louvre", 2: "2e Ardt - Bourse", 3: "3e Ardt - Temple", 4: "4e Ardt - Hôtel-de-Ville", 5: "5e Ardt - Panthéon",
    6: "6e Ardt - Luxembourg", 7: "7e Ardt - Palais-Bourbon", 8: "8e Ardt - Élysée", 9: "9e Ardt - Opéra", 10: "10e Ardt - Entrepôt",
    11: "11e Ardt - Popincourt", 12: "12e Ardt - Reuilly", 13: "13e Ardt - Gobelins", 14: "14e Ardt - Observatoire", 15: "15e Ardt - Vaugirard",
    16: "16e Ardt - Passy", 17: "17e Ardt - Batignolles-Monceau", 18: "18e Ardt - Buttes-Montmartre", 19: "19e Ardt - Buttes-Chaumont", 20: "20e Ardt - Ménilmontant",
}

def predict_all_arrondissement_prices(user_data: dict) -> pd.DataFrame:
    """
    Predicts the Airbnb price for the current listing configuration
    across all 20 Paris Arrondissements for heatmap visualization.
    """
    
    # 1. Create a base feature DataFrame using current user input
    base_df = build_airbnb_feature_df(user_data)
    all_arr_data = []
    
    # Map for the One-Hot column names (as used by the ML model)
    arr_map = {
        1: "Arrondissement_1er", 2: "Arrondissement_2e", 3: "Arrondissement_3e", 4: "Arrondissement_4e", 5: "Arrondissement_5e",
        6: "Arrondissement_6e", 7: "Arrondissement_7e", 8: "Arrondissement_8e", 9: "Arrondissement_9e", 10: "Arrondissement_10e",
        11: "Arrondissement_11e", 12: "Arrondissement_12e", 13: "Arrondissement_13e", 14: "Arrondissement_14e", 15: "Arrondissement_15e",
        16: "Arrondissement_16e", 17: "Arrondissement_17e", 18: "Arrondissement_18e", 19: "Arrondissement_19e", 20: "Arrondissement_20e",
    }
    arr_cols = list(arr_map.values())

    # 2. Loop through all 20 Arrondissements
    for arr_num in range(1, 21):
        
        # Clone base DF and zero out all existing Arrondissement columns
        df_single_arr = base_df.copy()
        for col in arr_cols:
            df_single_arr[col] = 0
            
        # Set the current Arrondissement's One-Hot column to 1
        current_arr_col = arr_map.get(arr_num)
        if current_arr_col:
            df_single_arr[current_arr_col] = 1
        
        # Predict the Log Price using the ML model
        price_log = model_airbnb_price.predict(df_single_arr)
        
        # Transform back from log scale and round to integer
        price_pred = np.expm1(float(price_log[0]))
        
        all_arr_data.append({
            "Arrondissement_Code": str(insee_map.get(arr_num)), 
            "Avg_Price_Apt": int(price_pred),
            "Arrondissement_Number": arr_num, 
            "Arrondissement_Name": arrondissement_names.get(arr_num) # New for heat-map
        })
        
    return pd.DataFrame(all_arr_data)




# Define Median Arrondissement for benchmarking (e.g., Arrondissement 10 is often near the median)
MEDIAN_ARR_NUM = 10 

def calculate_price_impact_kpis(user_data: dict, current_predicted_price: int):
    """
    Calculates key price impact metrics by predicting the price for specific
    benchmark scenarios based on the current user input.
    """
    
    # Get the base feature DataFrame (which already contains user's amenities, bedrooms, etc.)
    base_df = build_airbnb_feature_df(user_data)
    
    # 1. --- SCENARIO 1: PRICE IN MEDIAN ARRONDISSEMENT (Location Impact Benchmark) ---
    # We want to see the price of the USER's specific listing, but placed in a median location (Arrondissement 10).
    
    # Map for Arrondissement One-Hot columns
    arr_map = {
        1: "Arrondissement_1er", 2: "Arrondissement_2e", 3: "Arrondissement_3e", 4: "Arrondissement_4e", 5: "Arrondissement_5e",
        6: "Arrondissement_6e", 7: "Arrondissement_7e", 8: "Arrondissement_8e", 9: "Arrondissement_9e", 10: "Arrondissement_10e",
        11: "Arrondissement_11e", 12: "Arrondissement_12e", 13: "Arrondissement_13e", 14: "Arrondissement_14e", 15: "Arrondissement_15e",
        16: "Arrondissement_16e", 17: "Arrondissement_17e", 18: "Arrondissement_18e", 19: "Arrondissement_19e", 20: "Arrondissement_20e",
    }
    
    # Prepare the DF: Set all Arrondissement flags to 0
    df_location_neutral = base_df.copy()
    for col_name in arr_map.values():
        df_location_neutral[col_name] = 0
        
    # Set the Median Arrondissement flag to 1
    median_arr_col = arr_map.get(MEDIAN_ARR_NUM)
    if median_arr_col:
        df_location_neutral[median_arr_col] = 1

    # Predict the price for the user's listing if it were in the median location
    price_log_median_location = model_airbnb_price.predict(df_location_neutral)
    median_location_price = int(np.expm1(float(price_log_median_location[0])))
    
    
    # 2. --- SCENARIO 2: BASELINE CITY PRICE (Listing Quality Impact Benchmark) ---
    # We create a minimal baseline listing (1 bed, 1 bath, no superhost, in median Arrondissement)
    
    # Reset critical features in a copy of the median location DF
    df_baseline = df_location_neutral.copy()
    
    # Assuming baseline is the minimum meaningful input:
    df_baseline["host_is_superhost"] = 0
    df_baseline["host_listings_count"] = 1
    df_baseline["bedrooms"] = 1
    df_baseline["bathrooms_text"] = 1
    
    # Also set amenity flags to zero for the baseline comparison (Assuming amenity flags start at index 30 in airbnb_features)
    for i in range(29, len(airbnb_features)):
        df_baseline[airbnb_features[i]] = 0

    # Predict the price for the minimum baseline listing
    price_log_baseline = model_airbnb_price.predict(df_baseline)
    baseline_price = int(np.expm1(float(price_log_baseline[0])))
    
    
    # 3. --- CALCULATE FINAL KPIS ---
    
    # Location Impact: Difference between user's price in their Arrondissement and the price in the Median Arrondissement
    # High positive difference means the user's location adds value (e.g., Eiffel Tower view)
    location_impact = current_predicted_price - median_location_price
    
    # Quality Impact: Difference between user's listing price (in Median Arrondissement) and the absolute Baseline price
    # High positive difference means user's features (Superhost, amenities) add value
    quality_impact = median_location_price - baseline_price 
    
    return {
        "location_impact": location_impact,
        "quality_impact": quality_impact,
        "median_location_price": median_location_price,
        "baseline_price": baseline_price
    }
