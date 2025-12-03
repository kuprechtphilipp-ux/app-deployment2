import streamlit as st 
from stauth import Authenticate # allows to deal with authentification

#Define a sample user dictionary with credentials of all the users
#In a real-world scenario, you'd store this in a database or a secure file

users = { 
    "user1": {"name": "User One", "email": "user1@example.com", "password": "password123"},
    "user2": {"name": "User Two", "email": "user2@example.com", "password": "password456"}
}

authenticator = Authenticate(                  
    names=["User One", "User Two"],          
    usernames=["user1", "user2"],              
    passwords=["password123", "password456"],  
    cookie_name="my_auth_cookie",              
    key="my_key"                              
) 

def authenticate_user():  # Authenticate and log in a user using the pre-built authentication component
    name, authentication_status, username = authenticator.login("Login", "main") 
    if authentication_status:  # authentication worked
        st.success(f"Welcome {name}!") 
        return username # show username if it was authenticated
    elif authentication_status is False: # authentication failed
        st.error("Invalid username or password") 
    return None 
