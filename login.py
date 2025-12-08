import streamlit as st
import json
import os
from computations import label_to_amenity_col


# Define the path to the JSON file where user data is stored (refer to the Class - profiles)
PROFILES_DATA_PATH = "data/profiles.json"
    
# Load existing user data from JSON file
def load_data():
    if os.path.exists(PROFILES_DATA_PATH):
        with open(PROFILES_DATA_PATH, "r") as file:
            # Check if the file is empty
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # If the file is empty or not properly formatted, return an empty dict
                return {}
    else:
        return {}

# Save updated user data to JSON file
def save_data(data):
    with open(PROFILES_DATA_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Validate if the username and password are correct
def validate_user(username, password):
    data = load_data()
    if username in data and data[username]["password"] == password:
        return True
    return False

# Login Page Function
def login_page():
    st.title("Login Page")

    # Option for Login and Signup
    option = st.radio("Choose an option", ['Login', 'Sign Up'], index=0)

    if option == 'Login':
        # Create a form for Login
        with st.form(key='login_form'):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")

            if submit_button:
                    if validate_user(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                    
                        # IMPORTANT: Clear all old sidebar widget states
                        for k in list(st.session_state.keys()):
                            if k.startswith("sb_"):
                                del st.session_state[k]
                    
                        st.rerun()

                    else:
                        st.error("Invalid username or password.")
                else:
                    st.error("Please fill both username and password fields.")
    
    elif option == 'Sign Up':
        # Create a "form" for Sign Up --> do not use st.form otherwise no dynamic update is possible

            st.header("General Informations")
            
            # standard data
            new_username = st.text_input("Create a Username")
            new_password = st.text_input("Create a Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email Address")

            # Location informations
            st.header("Location of object in Paris")
            arrondissement = st.number_input("Arrondissement (1 to 20)", min_value=1, max_value=20, step=1)
            
            # property char
            st.header("Property Characteristics")
            
            # set first one as -- Select property type -- so that nothing is displayed below, first value is always what is displayed in the box
            
            room_type_options = ["-- Select property type --", "Entire home/apt", "Hotel room", "Private room", "Shared room"]

            room_type = st.selectbox("Object Type", room_type_options)

            if room_type == "Entire home/apt":
                bathrooms = st.number_input("Number of Bathrooms", min_value=1, step=1, value=1)
                bedrooms = st.number_input("Number of Bedrooms", min_value=1, step=1, value=1)

            # For other property types: set defaults but hide fields
            elif room_type in ["Hotel room", "Private room", "Shared room"]:
                bathrooms = 1
                bedrooms = 1
                #st.info("Bedrooms and bathrooms automatically set to 1 for this property type.")

            # If no valid type selected yet
            else:
                bathrooms = None
                bedrooms = None
                

            #st.subheader("Amenities")
            amenities = st.multiselect("Select Amenities", list(label_to_amenity_col.keys()))

            #st.subheader("Additional Information")

            num_rooms = st.number_input("Total number of Rooms", min_value=1, step=1)
            
            # airbnb related data
            st.header("Airbnb Related Informations")
            
            st.subheader("Host Information")
            host_is_superhost = st.checkbox("Are you a superhost?")
            host_listings_count = st.number_input("Number of Listings you have", min_value=0, step=1)
            host_identity_verified = st.checkbox("Are you verified on Airbnb?")
            
            """   Renting data not relevant - just used for comparison, can toogle stuff in from side bar in renting page - this was first idea, not needed anymore
            st.header("Renting Information")

            # need to use session state to be able to automatically show additional fields
            user_will_rent = st.checkbox("Will you rent?", value=st.session_state.get("rent", False))

            # Show extra inputs only if user will rent
            if user_will_rent:
                user_furnished = st.checkbox("Will your rent be furnished", value=st.session_state.get("furnished", False))
                user_number_rooms_rent = st.number_input("How many rooms does your rent have?",min_value=0,step=1, value=st.session_state.get("Number of rooms renting", 0))
            else:
                # set to default value
                user_furnished = False
                user_number_rooms_rent = 0
            """

            # if i click sign up button
            if st.button("Sign Up"):
                if new_username and new_password and new_password == confirm_password:
                    # Signup logic
                    data = load_data()
                    if new_username in data:
                        st.error("Username already exists!")
                    else:
                        # Save the new user info to the JSON file
                        data[new_username] = {
                            # Basic standard characteristics
                            "email": email,
                            "password": new_password,
                            
                            # Airbnb-related fields
                            "host_is_superhost": host_is_superhost,
                            "host_listings_count": host_listings_count,
                            "host_identity_verified": host_identity_verified,
                            "bathrooms": bathrooms,
                            "bedrooms": bedrooms,
                            "arrondissement": arrondissement,
                            "room_type": room_type,
                            "num_rooms": num_rooms,
                            "amenities": amenities,   # stored as a list
                            # for renting part
                            #"rent": user_will_rent,
                            #"Number of rooms renting": user_number_rooms_rent,
                            #"furnished": user_furnished  
                        }

                        # Save user profile
                        save_data(data)

                        st.success(f"Account created for {new_username}!")
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = new_username

                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    st.error("Please fill all fields.")
