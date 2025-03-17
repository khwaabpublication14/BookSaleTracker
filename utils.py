import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import io





def get_days_in_period(time_period):
    """Return the number of days in the selected time period."""
    if time_period == "Last 7 Days":
        return 7
    elif time_period == "Last 30 Days":
        return 30
    elif time_period == "Last 90 Days":
        return 90
    elif time_period == "Last Year":
        return 365
    else:  # All Time - approximate to 2 years
        return 730

def format_date(date_str):
    """Format date string to a more readable format."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%b %d, %Y')
    except:
        return date_str

def generate_csv_download(df, filename):
    """Generate a CSV download link for a DataFrame."""
    csv = df.to_csv(index=False)
    b64 = io.BytesIO(csv.encode())
    return b64

def calculate_growth_rate(current_value, previous_value):
    """Calculate growth rate between two values."""
    if previous_value == 0:
        return float('inf') if current_value > 0 else 0
    
    return ((current_value - previous_value) / previous_value) * 100

def get_performance_indicator(value):
    """Get a performance indicator (↑, ↓, or -) based on a value."""
    if value > 5:
        return "↑"
    elif value < -5:
        return "↓"
    else:
        return "-"

def get_performance_color(value):
    """Get a color code for performance indicators."""
    if value > 5:
        return "green"
    elif value < -5:
        return "red"
    else:
        return "orange"

def apply_date_filter(df, date_column, start_date, end_date):
    """Filter DataFrame by date range."""
    if not isinstance(df[date_column].iloc[0], pd.Timestamp):
        df[date_column] = pd.to_datetime(df[date_column])
    
    filtered_df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    return filtered_df

def get_book_title_by_id(book_id):
    """Get a book title for a given book ID."""
    if os.path.exists('data/books.csv'):
        books_df = pd.read_csv('data/books.csv')
        book = books_df[books_df['id'] == book_id]
        
        if not book.empty:
            return book.iloc[0]['title']
    
    return f"Book #{book_id}"
