import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import data_manager
import utils
import auth

# Set page config
st.set_page_config(
    page_title="Client Dashboard - Book Sales Tracker",
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
st.title("Client Dashboard")

# Get current username
username = st.session_state.username

# Get user books
user_books = data_manager.get_user_books(username)

if user_books.empty:
    st.warning("You don't have any books assigned to your account. Please contact your administrator.")
    st.stop()

# Dashboard layout
st.header("Sales Performance Dashboard")

# Filter controls
col1, col2, col3 = st.columns(3)

with col1:
    # Time period filter
    time_period = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"],
        index=1
    )

with col2:
    # Book filter
    book_titles = ["All Books"] + user_books['title'].tolist()
    selected_book = st.selectbox("Select Book", book_titles)

with col3:
    # Comparison option
    comparison = st.selectbox(
        "Comparison",
        ["None", "Previous Period", "Year-over-Year"]
    )

# Get filtered sales data
filtered_data = data_manager.filter_sales_by_time_period(username, time_period)

# Apply book filter if needed
if selected_book != "All Books" and not filtered_data.empty:
    filtered_data = filtered_data[filtered_data['title'] == selected_book]

# Key metrics section
st.subheader("Key Metrics")

if filtered_data.empty:
    st.info("No sales data available for the selected filters.")
else:
    # Calculate current period metrics
    total_sales = filtered_data['quantity'].sum()
    total_revenue = filtered_data['revenue'].sum()
    num_books_sold = len(filtered_data['book_id'].unique())
    avg_sale_price = total_revenue / total_sales if total_sales > 0 else 0
    total_royalties = filtered_data['royalty'].sum() if 'royalty' in filtered_data.columns else 0
    
    # Calculate comparison metrics if requested
    if comparison != "None":
        # Determine comparison period
        today = datetime.now()
        current_period_days = utils.get_days_in_period(time_period)
        
        if comparison == "Previous Period":
            # Previous period of same length
            prev_end_date = today - timedelta(days=current_period_days)
            prev_start_date = prev_end_date - timedelta(days=current_period_days)
        else:  # Year-over-Year
            # Same period last year
            prev_start_date = today - timedelta(days=365+current_period_days)
            prev_end_date = today - timedelta(days=365)
        
        # Get all sales data
        all_sales = data_manager.get_user_sales(username)
        
        if not all_sales.empty:
            # Convert date column to datetime if it's not already
            if not isinstance(all_sales['date'].iloc[0], pd.Timestamp):
                all_sales['date'] = pd.to_datetime(all_sales['date'])
            
            # Filter for previous period
            prev_period_data = all_sales[
                (all_sales['date'] >= pd.Timestamp(prev_start_date)) & 
                (all_sales['date'] <= pd.Timestamp(prev_end_date))
            ]
            
            # Apply book filter if needed
            if selected_book != "All Books":
                prev_period_data = prev_period_data[prev_period_data['title'] == selected_book]
            
            # Calculate previous period metrics
            prev_total_sales = prev_period_data['quantity'].sum() if not prev_period_data.empty else 0
            prev_total_revenue = prev_period_data['revenue'].sum() if not prev_period_data.empty else 0
            
            # Calculate growth rates
            sales_growth = utils.calculate_growth_rate(total_sales, prev_total_sales)
            revenue_growth = utils.calculate_growth_rate(total_revenue, prev_total_revenue)
        else:
            sales_growth = 0
            revenue_growth = 0
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if comparison != "None":
            st.metric(
                "Total Books Sold", 
                f"{total_sales:,}", 
                f"{sales_growth:.1f}% {utils.get_performance_indicator(sales_growth)}"
            )
        else:
            st.metric("Total Books Sold", f"{total_sales:,}")
    
    with col2:
        if comparison != "None":
            st.metric(
                "Total Revenue", 
                f"${total_revenue:,.2f}", 
                f"{revenue_growth:.1f}% {utils.get_performance_indicator(revenue_growth)}"
            )
        else:
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with col3:
        st.metric("Unique Books Sold", f"{num_books_sold}")
    
    with col4:
        st.metric("Average Sale Price", f"${avg_sale_price:.2f}")
    
    # Sales trend chart
    st.subheader("Sales Trend")
    
    sales_trend = data_manager.get_sales_trend(username, time_period)
    
    if not sales_trend.empty and selected_book == "All Books":
        fig = px.line(
            sales_trend, 
            x='date', 
            y='sales',
            title='Daily Book Sales',
            labels={'date': 'Date', 'sales': 'Books Sold'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    elif not filtered_data.empty and selected_book != "All Books":
        # Group by date for the specific book
        book_sales = filtered_data.copy()
        if isinstance(book_sales['date'].iloc[0], str):
            book_sales['date'] = pd.to_datetime(book_sales['date'])
        
        book_sales = book_sales.groupby(book_sales['date'].dt.date)['quantity'].sum().reset_index()
        book_sales.columns = ['date', 'sales']
        
        fig = px.line(
            book_sales, 
            x='date', 
            y='sales',
            title=f'Daily Sales: {selected_book}',
            labels={'date': 'Date', 'sales': 'Books Sold'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available for the selected filters.")
    
    # Two-column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Top selling books chart
        st.subheader("Top Selling Books")
        
        top_books = data_manager.get_top_books(username, time_period)
        
        if not top_books.empty:
            fig = px.bar(
                top_books,
                y='title',
                x='sales',
                title='Top Selling Books',
                labels={'title': 'Book Title', 'sales': 'Books Sold'},
                color='sales',
                color_continuous_scale=px.colors.sequential.Blues,
                orientation='h'
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No top books data available for the selected filters.")
    
    with col2:
        # Sales by genre chart
        st.subheader("Sales by Genre")
        
        genre_sales = data_manager.get_sales_by_genre(username, time_period)
        
        if not genre_sales.empty:
            fig = px.pie(
                genre_sales,
                values='sales',
                names='genre',
                title='Sales Distribution by Genre',
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No genre distribution data available for the selected filters.")
    
    # Detailed sales table
    st.subheader("Detailed Sales Data")
    
    if not filtered_data.empty:
        # Sort by date in descending order
        detailed_sales = filtered_data.sort_values('date', ascending=False)
        
        st.dataframe(
            detailed_sales[['date', 'title', 'quantity', 'price', 'revenue']],
            use_container_width=True,
            column_config={
                "date": "Date",
                "title": "Book Title",
                "quantity": "Copies Sold",
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f")
            }
        )
        
        # Export option
        if st.button("Export to CSV"):
            st.download_button(
                label="Download Sales Data",
                data=detailed_sales.to_csv(index=False).encode('utf-8'),
                file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No detailed sales data available for the selected filters.")
