import streamlit as st
import json
import os

# Paths for JSON files
PROFILE_DATA_PATH = "data/profiles.json"

# Ensure the data folder exists
if not os.path.exists("data"):
    os.makedirs("data")

def load_profile_data():
    """Load personal profile data from profiles.json."""
    if os.path.exists(PROFILE_DATA_PATH):
        try:
            with open(PROFILE_DATA_PATH, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            st.warning("The profile data file is corrupted or empty. Creating a new one.")
            return {}
    else:
        st.info("No profile data found. Initializing a new file.")
        return {}

def save_profile_data(data):
    """Save personal profile data to profiles.json."""
    with open(PROFILE_DATA_PATH, "w") as file:
        json.dump(data, file, indent=4)

def profile_page():
    st.title("User Profile")

    # Ensure username exists in session state
    if 'username' not in st.session_state:
        st.error("No username found in session state. Please log in again.")
        return

    username = st.session_state['username']
    st.subheader(f"Welcome, {username}!")

    st.write("""Update your information to allow us to be as precise as possible!""")
    
    # Load profile data
    profile_data = load_profile_data()

    # Initialize profile data for the user if it does not exist
    if username not in profile_data:
        st.warning("No profile found for the user. Initializing profile...")
        profile_data[username] = {
            "email": "",
            "password": "",
            # Airbnb-related fields
            "host_is_superhost": False,
            "host_listings_count": 0,
            "host_identity_verified": False,
            "bathrooms": 0,
            "bedrooms": 0,
            "arrondissement": 1,
            "room_type": "Private Room",
            "num_rooms": 1,
            "amenities": [],  # stored as a list
            #"rent": False,
            "Number of rooms renting": 2,
            "furnished": False
    }
    save_profile_data(profile_data)
    
    
    # update the values - if something changes and so on
    
    # Update Email
    new_email = st.text_input("New Email", value=profile_data[username].get("email", ""))
    if st.button("Update Email"):
        if new_email:
            profile_data[username]["email"] = new_email
            save_profile_data(profile_data)
            st.success(f"Email updated to {new_email}")
        else:
            st.error("Please enter a valid email.")

    # Update Password
    new_password = st.text_input("New Password", type="password", value=profile_data[username].get("password", ""))
    if st.button("Update Password"):
        if new_password:
            profile_data[username]["password"] = new_password
            save_profile_data(profile_data)
            st.success("Password updated.")
        else:
            st.error("Please enter a valid password.")

    # Update Host Superhost
    new_superhost = st.checkbox("Superhost?", value=profile_data[username].get("host_is_superhost", False))
    if st.button("Update Superhost Status"):
        profile_data[username]["host_is_superhost"] = new_superhost
        save_profile_data(profile_data)
        st.success(f"Superhost status updated to {new_superhost}")

    # Update Host Listings Count
    new_listings = st.number_input("Number of listings", min_value=0, value=profile_data[username].get("host_listings_count", 0))
    if st.button("Update Listings Count"):
        profile_data[username]["host_listings_count"] = new_listings
        save_profile_data(profile_data)
        st.success(f"Listings count updated to {new_listings}")

    # Update Host Identity Verified
    new_identity_verified = st.checkbox("Identity Verified?", value=profile_data[username].get("host_identity_verified", False))
    if st.button("Update Identity Verification"):
        profile_data[username]["host_identity_verified"] = new_identity_verified
        save_profile_data(profile_data)
        st.success(f"Identity verification updated to {new_identity_verified}")

    # Update Bathrooms
    new_bathrooms = st.number_input("Bathrooms", min_value=0, value=profile_data[username].get("bathrooms", 0))
    if st.button("Update Bathrooms"):
        profile_data[username]["bathrooms"] = new_bathrooms
        save_profile_data(profile_data)
        st.success(f"Bathrooms updated to {new_bathrooms}")

    # Update Bedrooms
    new_bedrooms = st.number_input("Bedrooms", min_value=0,value=profile_data[username].get("bedrooms", 0))
    if st.button("Update Bedrooms"):
        profile_data[username]["bedrooms"] = new_bedrooms
        save_profile_data(profile_data)
        st.success(f"Bedrooms updated to {new_bedrooms}")

    # Update Arrondissement
    new_arr = st.number_input("Arrondissement (1-20)", min_value=1, max_value=20, value=profile_data[username].get("arrondissement", 1))
    if st.button("Update Arrondissement"):
        profile_data[username]["arrondissement"] = new_arr
        save_profile_data(profile_data)
        st.success(f"Arrondissement updated to {new_arr}")

    # Update Room Type
    room_types = ["Entire home/apt", "Private room", "Shared room", "Hotel room"]
    new_room_type = st.selectbox("Room Type", room_types, index=room_types.index(profile_data[username].get("room_type", "Flat")))
    if st.button("Update Room Type"):
        profile_data[username]["room_type"] = new_room_type
        save_profile_data(profile_data)
        st.success(f"Room type updated to {new_room_type}")

    # Update Number of Rooms
    new_num_rooms = st.number_input("Number of rooms", min_value=1, value=profile_data[username].get("num_rooms", 1))
    if st.button("Update Num Rooms"):
        profile_data[username]["num_rooms"] = new_num_rooms
        save_profile_data(profile_data)
        st.success(f"Number of rooms updated to {new_num_rooms}")

    # Update Amenities (stored as list)
    available_amenities = [
        "WiFi", 
        "Kitchen", 
        "Bathtub", 
        "Balcony",           # <--- 'Balcony' added for debuging
        "Private entrance",
        "City skyline view",
        "Elevator", 
        "Air conditioning", 
        "Pets allowed", 
        "TV", 
        "Washer", "Dryer", "Heating", "Parking" # added for debugging
    ]

    # Update Amenities (stored as list)
    # ZUSAMMENFASSUNG ALLER VERWENDETEN AMENITIES ZUR BEHEBUNG DES STREAMLIT EXCEPTION:
    available_amenities = [
        "Kitchen", 
        "WiFi", 
        "Bathtub", 
        "Elevator", 
        "Air conditioning", 
        "Pets allowed", 
        "TV", 
        "Private entrance", 
        "Balcony", 
        "City skyline view",
        "Washer",    # Aus der alten Profil-Liste
        "Dryer",     # Aus der alten Profil-Liste
        "Heating",   # Aus der alten Profil-Liste
        "Parking"    # Aus der alten Profil-Liste
        # Stellen Sie sicher, dass keine Duplikate enthalten sind
    ]

    current_amenities = profile_data[username].get("amenities", [])

    new_amenities = st.multiselect("Select amenities", available_amenities, default=current_amenities)

    if st.button("Update Amenities"):
        profile_data[username]["amenities"] = new_amenities
        save_profile_data(profile_data)
        st.success("Amenities updated.")


    # Update Renting Status
    new_rent_status = st.checkbox("Do you rent your property?", value=profile_data[username].get("rent", False))
    if st.button("Update Renting Status"):
        profile_data[username]["rent"] = new_rent_status
        save_profile_data(profile_data)
        st.success(f"Renting status updated to {new_rent_status}")


    # Update Number of Rooms Renting
    new_renting_rooms = st.number_input("Number of rooms you rent", min_value=0, value=profile_data[username].get("Number of rooms renting", 0))
    if st.button("Update Rooms Renting"):
        profile_data[username]["Number of rooms renting"] = new_renting_rooms
        save_profile_data(profile_data)
        st.success(f"Number of rooms renting updated to {new_renting_rooms}")


    # Update Furnished Status 
    new_furnished_status = st.checkbox("Is the rented space furnished?", value=profile_data[username].get("furnished", False))
    if st.button("Update Furnished Status"):
        profile_data[username]["furnished"] = new_furnished_status
        save_profile_data(profile_data)
        st.success(f"Furnished status updated to {new_furnished_status}")

    
    # Logout button
    if st.button("Logout", key="logout_profile"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.session_state['email'] = None
        st.session_state['page'] = 'home'
        st.success("You have been logged out.")
        st.rerun()
