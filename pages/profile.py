import streamlit as st
import json
import os
from computations import label_to_amenity_col

# Path for JSON
PROFILE_DATA_PATH = "data/profiles.json"

# Ensure data folder exists
os.makedirs("data", exist_ok=True)


# ------------------------------------------------------------
# Helpers to load & save
# ------------------------------------------------------------
def load_profile_data():
    """Load personal profile data from profiles.json."""
    if os.path.exists(PROFILE_DATA_PATH):
        try:
            with open(PROFILE_DATA_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("Profile file corrupted — creating a new one.")
            return {}
    return {}


def save_profile_data(data):
    """Save personal profile data safely."""
    with open(PROFILE_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


# ------------------------------------------------------------
# MAIN PROFILE PAGE
# ------------------------------------------------------------
def profile_page():
    st.title("User Profile")

    # Check if logged in
    if "username" not in st.session_state:
        st.error("No username in session. Please log in again.")
        return

    username = st.session_state["username"]
    st.subheader(f"Welcome, {username}!")

    st.write("Update your information to allow us to be as precise as possible!")

    # Load or init profile data
    profile_data = load_profile_data()

    if username not in profile_data:
        # This should only happen on first login immediately after signup
        st.warning("No profile found. Creating a new profile...")
        profile_data[username] = {
            "email": "",
            "password": "",
            "host_is_superhost": False,
            "host_listings_count": 0,
            "host_identity_verified": False,
            "bathrooms": 1,
            "bedrooms": 1,
            "arrondissement": 1,
            "room_type": "Entire home/apt",
            "num_rooms": 1,
            "amenities": [],
            "rent": False,
            "Number of rooms renting": 0,
            "furnished": False,
        }
        save_profile_data(profile_data)

    user = profile_data[username]

    # ------------------------------------------------------------
    # 1. Update Email
    # ------------------------------------------------------------
    new_email = st.text_input("Email", value=user.get("email", ""))
    if st.button("Update Email"):
        profile_data[username]["email"] = new_email
        save_profile_data(profile_data)
        st.success("Email updated.")

    # ------------------------------------------------------------
    # 2. Update Password
    # ------------------------------------------------------------
    new_password = st.text_input("Password", type="password", value=user.get("password", ""))
    if st.button("Update Password"):
        profile_data[username]["password"] = new_password
        save_profile_data(profile_data)
        st.success("Password updated.")

    # ------------------------------------------------------------
    # 3. Airbnb Host Details
    # ------------------------------------------------------------
    st.subheader("Airbnb Host Information")

    new_superhost = st.checkbox("Superhost?", value=user.get("host_is_superhost", False))
    if st.button("Update Superhost Status"):
        profile_data[username]["host_is_superhost"] = new_superhost
        save_profile_data(profile_data)
        st.success("Superhost status updated.")

    new_listings = st.number_input(
        "Number of listings",
        min_value=0,
        value=user.get("host_listings_count", 0)
    )
    if st.button("Update Listings Count"):
        profile_data[username]["host_listings_count"] = new_listings
        save_profile_data(profile_data)
        st.success("Listings count updated.")

    new_verified = st.checkbox("Identity Verified?", value=user.get("host_identity_verified", False))
    if st.button("Update Identity Verification"):
        profile_data[username]["host_identity_verified"] = new_verified
        save_profile_data(profile_data)
        st.success("Identity verification updated.")

    # ------------------------------------------------------------
    # 4. Listing Property Characteristics
    # ------------------------------------------------------------
    st.subheader("Property Details")

    new_bathrooms = st.number_input("Bathrooms", min_value=0, value=user.get("bathrooms", 1))
    if st.button("Update Bathrooms"):
        profile_data[username]["bathrooms"] = new_bathrooms
        save_profile_data(profile_data)
        st.success("Bathrooms updated.")

    new_bedrooms = st.number_input("Bedrooms", min_value=0, value=user.get("bedrooms", 1))
    if st.button("Update Bedrooms"):
        profile_data[username]["bedrooms"] = new_bedrooms
        save_profile_data(profile_data)
        st.success("Bedrooms updated.")

    new_arr = st.number_input(
        "Arrondissement (1–20)",
        min_value=1,
        max_value=20,
        value=user.get("arrondissement", 1)
    )
    if st.button("Update Arrondissement"):
        profile_data[username]["arrondissement"] = new_arr
        save_profile_data(profile_data)
        st.success("Arrondissement updated.")

    room_types = ["Entire home/apt", "Private room", "Shared room", "Hotel room"]
    current_room_type = user.get("room_type", "Entire home/apt")
    new_room_type = st.selectbox("Room Type", room_types, index=room_types.index(current_room_type))
    if st.button("Update Room Type"):
        profile_data[username]["room_type"] = new_room_type
        save_profile_data(profile_data)
        st.success(f"Room type updated to {new_room_type}")

    new_num_rooms = st.number_input("Total number of rooms", min_value=1, value=user.get("num_rooms", 1))
    if st.button("Update Number of Rooms"):
        profile_data[username]["num_rooms"] = new_num_rooms
        save_profile_data(profile_data)
        st.success("Number of rooms updated.")

    # ------------------------------------------------------------
    # 5. Amenities — FULLY FIXED & ROBUST
    # ------------------------------------------------------------
    st.subheader("Amenities")

    available_amenities = list(label_to_amenity_col.keys())

    saved_amenities = user.get("amenities", [])

    # Normalize & filter saved amenities so they always exist in the options
    normalized = []
    for a in saved_amenities:
        if a in available_amenities:
            normalized.append(a)
        else:
            # Try case-insensitive match
            match = next((opt for opt in available_amenities if opt.lower() == a.lower()), None)
            if match:
                normalized.append(match)

    # Filter out invalid entries
    normalized = [a for a in normalized if a in available_amenities]

    new_amenities = st.multiselect("Select amenities", available_amenities, default=normalized)

    if st.button("Update Amenities"):
        profile_data[username]["amenities"] = new_amenities
        save_profile_data(profile_data)
        st.success("Amenities updated.")

    # ------------------------------------------------------------
    # 6. Renting Info
    # ------------------------------------------------------------
    st.subheader("Renting Information (optional)")

    new_rent_status = st.checkbox("Do you rent your property?", value=user.get("rent", False))
    if st.button("Update Renting Status"):
        profile_data[username]["rent"] = new_rent_status
        save_profile_data(profile_data)
        st.success("Rent status updated.")

    new_renting_rooms = st.number_input(
        "Rooms rented out",
        min_value=0,
        value=user.get("Number of rooms renting", 0)
    )
    if st.button("Update Rooms Renting"):
        profile_data[username]["Number of rooms renting"] = new_renting_rooms
        save_profile_data(profile_data)
        st.success("Rooms renting updated.")

    new_furnished = st.checkbox("Is the rented space furnished?", value=user.get("furnished", False))
    if st.button("Update Furnished Status"):
        profile_data[username]["furnished"] = new_furnished
        save_profile_data(profile_data)
        st.success("Furnished status updated.")

    # ------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------
    if st.button("Logout", key="logout_profile"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["page"] = "home"
        st.success("Logged out.")
        st.rerun()
