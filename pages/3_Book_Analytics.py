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
    page_title="Book Analytics - Book Sales Tracker",
    page_icon="📚",
    layout="wide"
)

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please log in to access this page.")
    st.stop()

# Ensure royalty data is updated
data_manager.update_sales_royalties()

# Display user info in sidebar
auth.show_user_info()

# Main content
st.title("Book Analytics")

# Get current username
username = st.session_state.username

# Get user books
user_books = data_manager.get_user_books(username)

if user_books.empty:
    st.warning("You don't have any books assigned to your account. Please contact your administrator.")
    st.stop()

# Book selection
selected_book_title = st.selectbox("Select Book for Analysis", user_books['title'].tolist())

# Get selected book details
selected_book = user_books[user_books['title'] == selected_book_title].iloc[0]
book_id = selected_book['id']

# Time period selection
time_period = st.selectbox(
    "Select Time Period",
    ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "All Time"],
    index=1
)

# Get all sales data for the user
all_sales = data_manager.get_user_sales(username)

# Filter for selected book
book_sales = all_sales[all_sales['book_id'] == book_id] if not all_sales.empty else pd.DataFrame()

if book_sales.empty:
    st.info(f"No sales data available for '{selected_book_title}'.")
    st.stop()

# Filter by time period
filtered_sales = data_manager.filter_sales_by_time_period(username, time_period)
filtered_sales = filtered_sales[filtered_sales['book_id'] == book_id] if not filtered_sales.empty else pd.DataFrame()

# Book details card
st.header("Book Details")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"**Title:** {selected_book['title']}")
    st.markdown(f"**Author:** {selected_book['author']}")
    st.markdown(f"**Genre:** {selected_book['genre']}")

with col2:
    st.markdown(f"**Price:** ₹{utils.convert_usd_to_inr(selected_book['price']):.2f}")
    st.markdown(f"**Publication Date:** {selected_book['publication_date']}")
    if 'isbn' in selected_book:
        st.markdown(f"**ISBN:** {selected_book['isbn']}")

with col3:
    total_sold = book_sales['quantity'].sum()
    total_revenue = book_sales['revenue'].sum()
    total_royalties = book_sales['royalty'].sum() if 'royalty' in book_sales.columns else 0
    st.markdown(f"**Total Copies Sold:** {total_sold:,}")
    st.markdown(f"**Total Revenue:** ₹{utils.convert_usd_to_inr(total_revenue):,.2f}")
    if 'royalty_percentage' in selected_book:
        st.markdown(f"**Royalty Rate:** {selected_book['royalty_percentage']}%")
    if 'royalty' in book_sales.columns:
        st.markdown(f"**Total Royalties Earned:** ₹{utils.convert_usd_to_inr(total_royalties):,.2f}")

# Sales metrics for the selected period
st.header(f"Sales Metrics ({time_period})")

if filtered_sales.empty:
    st.info(f"No sales data available for '{selected_book_title}' in the selected time period.")
else:
    # Calculate metrics for the selected period
    period_total_sold = filtered_sales['quantity'].sum()
    period_total_revenue = filtered_sales['revenue'].sum()
    period_total_royalties = filtered_sales['royalty'].sum() if 'royalty' in filtered_sales.columns else 0

    # Calculate previous period metrics for comparison
    current_period_days = utils.get_days_in_period(time_period)
    today = datetime.now()

    # Previous period of same length
    prev_end_date = today - timedelta(days=current_period_days)
    prev_start_date = prev_end_date - timedelta(days=current_period_days)

    # Convert date column to datetime if needed
    if not isinstance(book_sales['date'].iloc[0], pd.Timestamp):
        book_sales['date'] = pd.to_datetime(book_sales['date'])

    # Filter for previous period
    prev_period_sales = book_sales[
        (book_sales['date'] >= pd.Timestamp(prev_start_date)) & 
        (book_sales['date'] <= pd.Timestamp(prev_end_date))
    ]

    # Calculate metrics for previous period
    prev_period_sold = prev_period_sales['quantity'].sum() if not prev_period_sales.empty else 0
    prev_period_revenue = prev_period_sales['revenue'].sum() if not prev_period_sales.empty else 0
    prev_period_royalties = prev_period_sales['royalty'].sum() if not prev_period_sales.empty and 'royalty' in prev_period_sales.columns else 0

    # Calculate growth rates
    sales_growth = utils.calculate_growth_rate(period_total_sold, prev_period_sold)
    revenue_growth = utils.calculate_growth_rate(period_total_revenue, prev_period_revenue)
    royalty_growth = utils.calculate_growth_rate(period_total_royalties, prev_period_royalties) if 'royalty' in filtered_sales.columns else 0

    # Display metrics in columns
    if 'royalty' in filtered_sales.columns:
        col1, col2, col3, col4, col5 = st.columns(5)
    else:
        col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Copies Sold", 
            f"{period_total_sold:,}", 
            f"{sales_growth:.1f}% {utils.get_performance_indicator(sales_growth)}"
        )

    with col2:
        st.metric(
            "Revenue", 
            f"₹{utils.convert_usd_to_inr(period_total_revenue):,.2f}", 
            f"{revenue_growth:.1f}% {utils.get_performance_indicator(revenue_growth)}"
        )

    if 'royalty' in filtered_sales.columns:
        with col3:
            st.metric(
                "Royalties Earned", 
                f"₹{utils.convert_usd_to_inr(period_total_royalties):,.2f}", 
                f"{royalty_growth:.1f}% {utils.get_performance_indicator(royalty_growth)}"
            )

        with col4:
            avg_daily_sales = period_total_sold / current_period_days
            st.metric("Avg. Daily Sales", f"{avg_daily_sales:.1f}")

        with col5:
            avg_price = period_total_revenue / period_total_sold if period_total_sold > 0 else 0
            st.metric("Avg. Sale Price", f"₹{utils.convert_usd_to_inr(avg_price):.2f}")
    else:
        with col3:
            avg_daily_sales = period_total_sold / current_period_days
            st.metric("Avg. Daily Sales", f"{avg_daily_sales:.1f}")

        with col4:
            avg_price = period_total_revenue / period_total_sold if period_total_sold > 0 else 0
            st.metric("Avg. Sale Price", f"₹{utils.convert_usd_to_inr(avg_price):.2f}")

    # Sales trend chart
    st.subheader("Sales Trend")

    # Make sure dates are datetime objects
    if not isinstance(filtered_sales['date'].iloc[0], pd.Timestamp):
        filtered_sales['date'] = pd.to_datetime(filtered_sales['date'])

    # Group by date for the trend chart
    sales_by_date = filtered_sales.groupby(filtered_sales['date'].dt.date)['quantity'].sum().reset_index()
    sales_by_date.columns = ['date', 'sales']

    # Sort by date
    sales_by_date = sales_by_date.sort_values('date')

    # Fill in missing dates with zero sales
    date_range = pd.date_range(sales_by_date['date'].min(), sales_by_date['date'].max())
    full_date_df = pd.DataFrame({'date': date_range})
    full_date_df['date'] = full_date_df['date'].dt.date

    sales_trend = pd.merge(full_date_df, sales_by_date, on='date', how='left')
    sales_trend['sales'] = sales_trend['sales'].fillna(0)

    fig = px.line(
        sales_trend, 
        x='date', 
        y='sales',
        title=f'Daily Sales: {selected_book_title}',
        labels={'date': 'Date', 'sales': 'Copies Sold'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Sales distribution charts
    col1, col2 = st.columns(2)

    with col1:
        # Monthly distribution
        st.subheader("Monthly Sales Distribution")

        # Extract month from date and group by month
        filtered_sales['month'] = filtered_sales['date'].dt.strftime('%b')
        filtered_sales['month_num'] = filtered_sales['date'].dt.month

        monthly_sales = filtered_sales.groupby(['month', 'month_num'])['quantity'].sum().reset_index()
        monthly_sales = monthly_sales.sort_values('month_num')

        fig = px.bar(
            monthly_sales,
            x='month',
            y='quantity',
            title='Monthly Sales Distribution',
            labels={'month': 'Month', 'quantity': 'Copies Sold'},
            color='quantity',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Day of week distribution
        st.subheader("Day of Week Sales Distribution")

        # Extract day of week from date and group by day
        filtered_sales['day'] = filtered_sales['date'].dt.day_name()
        filtered_sales['day_num'] = filtered_sales['date'].dt.dayofweek

        daily_sales = filtered_sales.groupby(['day', 'day_num'])['quantity'].sum().reset_index()
        daily_sales = daily_sales.sort_values('day_num')

        fig = px.bar(
            daily_sales,
            x='day',
            y='quantity',
            title='Day of Week Sales Distribution',
            labels={'day': 'Day', 'quantity': 'Copies Sold'},
            color='quantity',
            color_continuous_scale=px.colors.sequential.Blues
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Sales data table
    st.subheader("Detailed Sales Data")

    # Sort by date in descending order
    detailed_sales = filtered_sales.sort_values('date', ascending=False)

    # Prepare display columns and configuration
    display_columns = ['date', 'quantity', 'price', 'revenue']
    column_config = {
        "date": "Date",
        "quantity": "Copies Sold",
        "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
        "revenue": st.column_config.NumberColumn("Revenue", format="₹%.2f")
    }

    # Add royalty column if it exists
    if 'royalty' in detailed_sales.columns:
        display_columns.append('royalty')
        column_config["royalty"] = st.column_config.NumberColumn("Royalty", format="₹%.2f")

    st.dataframe(
        detailed_sales[display_columns],
        use_container_width=True,
        column_config=column_config
    )

    # Export option
    if st.button("Export to CSV"):
        st.download_button(
            label="Download Sales Data",
            data=detailed_sales.to_csv(index=False).encode('utf-8'),
            file_name=f"{selected_book_title.replace(' ', '_')}_sales_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # Sales performance summary
    st.subheader("Performance Summary")

    # Calculate performance metrics
    avg_daily_sales = period_total_sold / current_period_days
    sales_growth_indicator = utils.get_performance_indicator(sales_growth)
    sales_growth_color = utils.get_performance_color(sales_growth)

    # Calculate royalty metrics if available - this was moved earlier in the code
    royalty_growth = 0
    royalty_growth_indicator = ""

    if 'royalty' in filtered_sales.columns:
        # Period total royalties is already calculated earlier
        # Just prepare the indicator here to fix LSP issues
        royalty_growth_indicator = utils.get_performance_indicator(royalty_growth)

    # Display performance summary
    summary_text = f"""
    - **{selected_book_title}** sold **{period_total_sold:,}** copies in the selected period.
    - The sales performance is **{sales_growth:.1f}%** {sales_growth_indicator} compared to the previous period.
    - The book generates an average of **{avg_daily_sales:.1f}** sales per day.
    - Total revenue for the period: **₹{utils.convert_usd_to_inr(period_total_revenue):,.2f}**
    """

    # Add royalty information to summary if available
    if 'royalty' in filtered_sales.columns:
        royalty_text = f"""
    - Total royalties earned: **₹{utils.convert_usd_to_inr(period_total_royalties):,.2f}**
    - Royalty performance is **{royalty_growth:.1f}%** {royalty_growth_indicator} compared to the previous period.
        """
        summary_text += royalty_text

    st.markdown(summary_text)

    # Performance rating
    if sales_growth > 20:
        st.success("⭐⭐⭐⭐⭐ Excellent performance! Sales are growing strongly.")
    elif sales_growth > 5:
        st.success("⭐⭐⭐⭐ Good performance. Sales are steadily increasing.")
    elif sales_growth > -5:
        st.info("⭐⭐⭐ Stable performance. Sales are holding steady.")
    elif sales_growth > -20:
        st.warning("⭐⭐ Performance needs attention. Sales are slightly decreasing.")
    else:
        st.error("⭐ Poor performance. Sales are declining significantly.")