import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import auth
import data_manager
import utils

# Configure the page
st.set_page_config(
    page_title="Khwaab Publication - Book Sales Tracker",
    page_icon="attached_assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display logo in sidebar
with st.sidebar:
    st.image("attached_assets/logo.png", width=200)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'first_load' not in st.session_state:
    st.session_state.first_load = True
    # Initialize the data on first load
    data_manager.initialize_data()
    # Update sales data with royalty calculations if needed
    data_manager.update_sales_royalties()

# Authentication
if not st.session_state.authenticated:
    auth.show_login_page()
else:
    # Show the home page with overview dashboard
    st.title(f"Welcome to Khwaab Publication Book Sales Tracker, {st.session_state.username}!")
    
    # Display role-specific information
    if st.session_state.user_role == "admin":
        st.info("You are logged in as an administrator. You can manage books, update sales data, and view all client information.")
    else:
        st.info("You are logged in as a client. You can view your book sales data and analytics.")
    
    # Get all books for the current user
    user_books = data_manager.get_user_books(st.session_state.username)
    
    if len(user_books) == 0:
        if st.session_state.user_role == "admin":
            st.warning("No books found in the system. Go to the Admin Panel to add books.")
        else:
            st.warning("You don't have any books assigned to your account. Please contact your administrator.")
    else:
        # Overview metrics
        st.header("Sales Overview")
        
        # Filter data by time period
        time_period = st.selectbox(
            "Select Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"],
            index=1
        )
        
        filtered_data = data_manager.filter_sales_by_time_period(st.session_state.username, time_period)
        
        if filtered_data.empty:
            st.warning("No sales data available for the selected time period.")
        else:
            # Calculate metrics
            total_sales = filtered_data['quantity'].sum()
            total_revenue = (filtered_data['quantity'] * filtered_data['price']).sum()
            avg_daily_sales = total_sales / utils.get_days_in_period(time_period)
            
            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Books Sold", f"{total_sales:,}")
            with col2:
                st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
            with col3:
                st.metric("Avg. Daily Sales", f"{avg_daily_sales:.1f}")
            
            # Sales over time chart
            st.subheader("Sales Trend")
            sales_trend = data_manager.get_sales_trend(st.session_state.username, time_period)
            
            fig = px.line(
                sales_trend, 
                x='date', 
                y='sales',
                title='Book Sales Over Time',
                labels={'date': 'Date', 'sales': 'Books Sold'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top selling books
            st.subheader("Top Selling Books")
            top_books = data_manager.get_top_books(st.session_state.username, time_period, limit=5)
            
            fig = px.bar(
                top_books,
                x='title',
                y='sales',
                title='Top Selling Books',
                labels={'title': 'Book Title', 'sales': 'Books Sold'},
                color='sales',
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Recent sales table
            st.subheader("Recent Sales")
            recent_sales = data_manager.get_recent_sales(st.session_state.username, limit=10)
            
            if not recent_sales.empty:
                st.dataframe(
                    recent_sales[['date', 'title', 'quantity', 'price', 'revenue']],
                    use_container_width=True,
                    column_config={
                        "date": "Date",
                        "title": "Book Title",
                        "quantity": "Copies Sold",
                        "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                        "revenue": st.column_config.NumberColumn("Revenue", format="₹%.2f")
                    }
                )
            else:
                st.info("No recent sales data available.")
