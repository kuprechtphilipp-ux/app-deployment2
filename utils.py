# general helper functions

#import css file 
import streamlit as st
import os


# Example helper function
def is_authenticated(username, password):
    return username == "admin" and password == "password"


def import_css(css_file="style.css"): #import css in streamlit 
  
    try:
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS FILE '{css_file}' was not found.")               #lines 11-17: source Chat GPT