import streamlit as st
import json
import os
from computations import label_to_amenity_col

# Path for storing user profiles
PROFILES_DATA_PATH = "data/profiles.json"


# -------------------------
# Data handling utilities
# -------------------------
def load_data():
    """Load all user profiles from JSON file."""
    if os.path.exists(PROFILES_DATA_PATH):
        try:
            with open(PROFILES_DATA_PATH, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}  # corrupt file → treat as empty
    return {}


def save_data(data):
    """Save all user profiles to JSON."""
    with open(PROFILES_DATA_PATH, "w") as file:
        json.dump(data, file, indent=4)


def validate_user(username, password):
    """Check if user credentials match."""
    data = load_data()
    return username in data and data[username]["password"] == password


# ---------------------------------------------------
# LOGIN + SIGN-UP PAGE
# ---------------------------------------------------
def login_page():
    st.title("Login Page")

    option = st.radio("Choose an option", ["Login", "Sign Up"], index=0)

    # ---------------------------------------------------
    # LOGIN SECTION
    # ---------------------------------------------------
    if option == "Login":
        with st.form(key="login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                if not username or not password:
                    st.error("Please fill both username and password fields.")
                else:
                    if validate_user(username, password):
                        # Store login information
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = username

                        # Clear old saved sidebar widget states after switch users
                        for k in list(st.session_state.keys()):
                            if k.startswith("sb_"):
                                del st.session_state[k]

                        st.rerun()

                    else:
                        st.error("Invalid username or password.")

    # ---------------------------------------------------
    # SIGN-UP SECTION
    # ---------------------------------------------------
    elif option == "Sign Up":

        st.header("General Informations")
        new_username = st.text_input("Create a Username")
        new_password = st.text_input("Create a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        email = st.text_input("Email Address")

        st.header("Location of object in Paris")
        arrondissement = st.number_input("Arrondissement (1 to 20)", min_value=1, max_value=20, step=1)

        st.header("Property Characteristics")
        room_type_options = [
            "-- Select property type --",
            "Entire home/apt",
            "Hotel room",
            "Private room",
            "Shared room",
        ]

        room_type = st.selectbox("Object Type", room_type_options)

        if room_type == "Entire home/apt":
            bathrooms = st.number_input("Number of Bathrooms", min_value=1, value=1, step=1)
            bedrooms = st.number_input("Number of Bedrooms", min_value=1, value=1, step=1)
        elif room_type in ["Hotel room", "Private room", "Shared room"]:
            bathrooms = 1
            bedrooms = 1
        else:
            bathrooms = None
            bedrooms = None

        amenities = st.multiselect("Select Amenities", list(label_to_amenity_col.keys()))

        num_rooms = st.number_input("Total number of Rooms", min_value=1, step=1)

        st.header("Airbnb Related Informations")
        host_is_superhost = st.checkbox("Are you a superhost?")
        host_listings_count = st.number_input("Number of Listings you have", min_value=0, step=1)
        host_identity_verified = st.checkbox("Are you verified on Airbnb?")

        # ---------------------------------------------------
        # SIGN-UP BUTTON
        # ---------------------------------------------------
        if st.button("Sign Up"):
            if not new_username or not new_password or not confirm_password:
                st.error("Please fill all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                data = load_data()
                if new_username in data:
                    st.error("Username already exists!")
                else:
                    data[new_username] = {
                        "email": email,
                        "password": new_password,

                        "host_is_superhost": host_is_superhost,
                        "host_listings_count": host_listings_count,
                        "host_identity_verified": host_identity_verified,
                        "bathrooms": bathrooms,
                        "bedrooms": bedrooms,
                        "arrondissement": arrondissement,
                        "room_type": room_type,
                        "num_rooms": num_rooms,
                        "amenities": amenities,  # stored as list
                    }

                    save_data(data)

                    st.success(f"Account created for {new_username}!")
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = new_username
                    st.rerun()
