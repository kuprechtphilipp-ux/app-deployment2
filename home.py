import streamlit as st 

# main page that loads once website is started, the one where you can sign up or login, with our logo

def home_page():  
    st.title("Welcome to the airbnb pricing app") 
    st.markdown( """## Find the best price to rent your flat/room!""") 

    logo = "images/logo.png" # our logo, stored in images, maybe change logo or create one of our own
    col1, col2, col3 = st.columns([1, 2, 1]) # to center the image
    with col2: 
        st.image(logo, width=380) # logo visualization

    #Login/Sign Up button:
    if st.session_state['logged_in'] == False: # Check if the user is not authenticated (False). This is done using st.session_state, a special dictionary that allows you to store and manage the status of the site. “logged_in” is the key and indicates whether the user is authentic = True or not = False.
        if st.button("Login / Sign Up", key="login_signup", help="Click to log in or sign up", use_container_width=True): #login/sign up button
            st.session_state['page'] = 'login' #update the session state to be able to go to login page 
            st.rerun() 

    st.markdown(
        """ 
        ## About Our Platform
        Optimize your Airbnb pricing with confidence! <br>
        Our platform helps hosts determine the most profitable nightly rate by analyzing key factors such as cleaning fees, rent, utility costs, occupancy expectations, and market trends. Easily track your expenses, understand your break-even point, and receive smart pricing suggestions to maximize revenue while staying competitive. Make data-driven decisions and boost your earnings with an intelligent, host-friendly pricing assistant.
        """,
        unsafe_allow_html=True
    )


    


