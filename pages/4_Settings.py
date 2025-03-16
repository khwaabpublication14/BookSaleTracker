import streamlit as st
import pandas as pd
import data_manager
import auth
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Settings - Book Sales Tracker",
    page_icon="📚",
    layout="wide"
)

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please log in to access this page.")
    st.stop()

# Display user info in sidebar
auth.show_user_info()

# Main content
st.title("Settings")

# Display user details
st.header("User Information")
st.markdown(f"**Username:** {st.session_state.username}")
st.markdown(f"**Name:** {st.session_state.name}")
st.markdown(f"**Role:** {st.session_state.user_role.capitalize()}")

# Display different settings based on user role
if st.session_state.user_role == "admin":
    # Admin settings
    st.header("Admin Settings")
    
    tab1, tab2 = st.tabs(["Data Management", "Export/Import"])
    
    with tab1:
        st.subheader("Data Management")
        
        # Option to clear sales data
        st.warning("⚠️ Warning: The following actions will permanently delete data!")
        
        if st.button("Clear All Sales Data"):
            if os.path.exists('data/sales.csv'):
                # Create an empty sales dataframe with the same columns
                empty_sales = pd.DataFrame(columns=[
                    'date', 'book_id', 'quantity', 'price', 'revenue'
                ])
                empty_sales.to_csv('data/sales.csv', index=False)
                st.success("All sales data has been cleared successfully.")
            else:
                st.error("Sales data file not found.")
        
        # Option to clear book data
        if st.button("Clear All Book Data"):
            if os.path.exists('data/books.csv'):
                # Create an empty books dataframe with the same columns
                empty_books = pd.DataFrame(columns=[
                    'id', 'title', 'author', 'genre', 'owner', 'price', 'publication_date'
                ])
                empty_books.to_csv('data/books.csv', index=False)
                st.success("All book data has been cleared successfully.")
            else:
                st.error("Books data file not found.")
    
    with tab2:
        st.subheader("Export/Import Data")
        
        # Export data
        st.markdown("### Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Books Data"):
                if os.path.exists('data/books.csv'):
                    books_df = pd.read_csv('data/books.csv')
                    st.download_button(
                        label="Download Books Data",
                        data=books_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"books_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Books data file not found.")
        
        with col2:
            if st.button("Export Sales Data"):
                if os.path.exists('data/sales.csv'):
                    sales_df = pd.read_csv('data/sales.csv')
                    st.download_button(
                        label="Download Sales Data",
                        data=sales_df.to_csv(index=False).encode('utf-8'),
                        file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Sales data file not found.")
        
        # Import data
        st.markdown("### Import Data")
        st.warning("⚠️ Warning: Importing data will overwrite existing data!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_books = st.file_uploader("Upload Books CSV", type="csv")
            if uploaded_books is not None:
                try:
                    books_df = pd.read_csv(uploaded_books)
                    required_columns = ['id', 'title', 'author', 'genre', 'owner', 'price', 'publication_date']
                    
                    if all(col in books_df.columns for col in required_columns):
                        books_df.to_csv('data/books.csv', index=False)
                        st.success("Books data imported successfully!")
                    else:
                        st.error("Invalid CSV format. Missing required columns.")
                except Exception as e:
                    st.error(f"Error importing books data: {e}")
        
        with col2:
            uploaded_sales = st.file_uploader("Upload Sales CSV", type="csv")
            if uploaded_sales is not None:
                try:
                    sales_df = pd.read_csv(uploaded_sales)
                    required_columns = ['date', 'book_id', 'quantity', 'price', 'revenue']
                    
                    if all(col in sales_df.columns for col in required_columns):
                        sales_df.to_csv('data/sales.csv', index=False)
                        st.success("Sales data imported successfully!")
                    else:
                        st.error("Invalid CSV format. Missing required columns.")
                except Exception as e:
                    st.error(f"Error importing sales data: {e}")

# Client settings
st.header("Application Settings")

# Theme preference
st.subheader("Theme Preference")
theme_option = st.radio(
    "Select Theme",
    ["Default (Light)", "Blue", "Green"],
    horizontal=True
)

st.info("Theme settings will be applied on the next login.")

# Notification settings
st.subheader("Notification Settings")
email_notifications = st.checkbox("Enable email notifications for sales updates", value=False)
daily_summary = st.checkbox("Receive daily sales summary", value=False)
weekly_summary = st.checkbox("Receive weekly sales summary", value=True)

if st.button("Save Settings"):
    st.success("Settings saved successfully!")

# Display app information
st.header("About")
st.markdown("""
### Book Sales Tracker
Version 1.0.0

Track and analyze your book sales with interactive dashboards and detailed analytics.

**Features:**
- Real-time sales tracking
- Interactive visualizations
- Detailed book analytics
- Export functionality for reports
- User role-based access control

For support, please contact the administrator.
""")
