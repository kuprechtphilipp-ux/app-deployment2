import streamlit as st
from home import home_page
from login import login_page
from pages.profile import profile_page  
from pages.airbnb_page import airbnb_page
from pages.renting_page import renting_page
from pages.comparison import comparison_page
from utils import import_css  




def main():
    # Initialize session state for 'logged_in' and 'page'
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'  # Set default page to 'home', the one with our logo

    if not st.session_state['logged_in']:  # If the user is not logged in
        if st.session_state['page'] == 'home':
            home_page()  # Show home page
        elif st.session_state['page'] == 'login':
            login_page()  # Show login page
    else:  # If the user is logged in, show the dashboard
        # Sidebar navigation for logged-in users
        page = st.sidebar.radio("Select a page", [
            "Airbnb", 
            "Renting",
            "Comparison",
            "Profile",  # Add profile to the sidebar
        ])

        # Update session state to reflect the selected page
        st.session_state['page'] = page

        if page == "Airbnb":
            airbnb_page()
        elif page == "Renting":
            renting_page()
        elif page == "Comparison":
            comparison_page()
        elif page == "Profile": 
            profile_page()

if __name__ == "__main__":
    main()
