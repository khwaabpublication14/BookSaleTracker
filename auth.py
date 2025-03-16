import streamlit as st
import pandas as pd
import hashlib
import os
import data_manager

def initialize_users():
    """Initialize default users if they don't exist."""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if not os.path.exists('data/users.csv'):
        # Create default admin and client users
        users_data = {
            'username': ['admin', 'client1', 'client2'],
            'password': [
                hash_password('admin123'),
                hash_password('client123'),
                hash_password('client123')
            ],
            'role': ['admin', 'client', 'client'],
            'name': ['Administrator', 'John Smith', 'Emily Johnson']
        }
        
        users_df = pd.DataFrame(users_data)
        users_df.to_csv('data/users.csv', index=False)
        return users_df
    else:
        return pd.read_csv('data/users.csv')

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username, password):
    """Authenticate user with username and password."""
    users_df = initialize_users()
    
    # Check if username exists
    user = users_df[users_df['username'] == username]
    if user.empty:
        return False, None, None
    
    # Check password
    hashed_password = hash_password(password)
    if user.iloc[0]['password'] == hashed_password:
        return True, user.iloc[0]['role'], user.iloc[0]['name']
    
    return False, None, None

def show_login_page():
    """Display login form and handle authentication."""
    st.title("Book Sales Tracker - Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")
        
        if submit_button:
            is_authenticated, role, name = authenticate(username, password)
            
            if is_authenticated:
                st.session_state.authenticated = True
                st.session_state.user_role = role
                st.session_state.username = username
                st.session_state.name = name
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")
    
    st.info("Default credentials for testing:")
    st.markdown("- Admin: username=`admin`, password=`admin123`")
    st.markdown("- Client: username=`client1`, password=`client123`")

def logout():
    """Log out user by resetting session state."""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.name = None
    st.rerun()

def show_user_info():
    """Display current user info in the sidebar."""
    if st.session_state.authenticated:
        with st.sidebar:
            st.write(f"Logged in as: **{st.session_state.name}**")
            st.write(f"Role: **{st.session_state.user_role.capitalize()}**")
            if st.button("Log Out"):
                logout()
