import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import utils

def initialize_data():
    """Initialize default data if it doesn't exist."""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize books data
    if not os.path.exists('data/books.csv'):
        books_data = {
            'id': [1, 2, 3, 4, 5],
            'title': [
                'The Art of Programming',
                'Data Science Fundamentals',
                'Business Strategy',
                'Marketing 101',
                'Leadership Principles'
            ],
            'author': [
                'John Doe',
                'Jane Smith',
                'Robert Johnson',
                'Emily Williams',
                'Michael Brown'
            ],
            'genre': [
                'Technology',
                'Technology',
                'Business',
                'Marketing',
                'Business'
            ],
            'owner': [
                'client1',
                'client1',
                'client2',
                'client2',
                'client2'
            ],
            'price': [
                29.99,
                24.99,
                19.99,
                14.99,
                22.99
            ],
            'publication_date': [
                '2020-03-15',
                '2021-07-22',
                '2019-11-08',
                '2022-01-30',
                '2020-09-12'
            ]
        }
        
        books_df = pd.DataFrame(books_data)
        books_df.to_csv('data/books.csv', index=False)
    
    # Initialize sales data
    if not os.path.exists('data/sales.csv'):
        # Generate sales data for the past year
        sales_data = []
        today = datetime.now()
        
        books_df = pd.read_csv('data/books.csv')
        book_ids = books_df['id'].tolist()
        
        # Generate random sales data for the past year
        for _ in range(500):  # Generate 500 sales records
            book_id = np.random.choice(book_ids)
            book_row = books_df[books_df['id'] == book_id].iloc[0]
            
            # Random date within the past year
            days_ago = np.random.randint(0, 365)
            sale_date = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # Random quantity between 1 and 10
            quantity = np.random.randint(1, 11)
            
            sales_data.append({
                'date': sale_date,
                'book_id': book_id,
                'quantity': quantity,
                'price': book_row['price'],
                'revenue': quantity * book_row['price']
            })
        
        sales_df = pd.DataFrame(sales_data)
        sales_df.to_csv('data/sales.csv', index=False)

def get_books():
    """Get all books from the dataset."""
    if os.path.exists('data/books.csv'):
        return pd.read_csv('data/books.csv')
    return pd.DataFrame()

def get_user_books(username):
    """Get books owned by a specific user or all books for admin."""
    books_df = get_books()
    
    if books_df.empty:
        return pd.DataFrame()
    
    # If admin, return all books, otherwise filter by owner
    if username == 'admin':
        return books_df
    else:
        return books_df[books_df['owner'] == username]

def get_sales():
    """Get all sales from the dataset."""
    if os.path.exists('data/sales.csv'):
        return pd.read_csv('data/sales.csv')
    return pd.DataFrame()

def add_book(title, author, genre, owner, price, publication_date):
    """Add a new book to the dataset."""
    books_df = get_books()
    
    # Generate new ID
    if books_df.empty:
        new_id = 1
    else:
        new_id = books_df['id'].max() + 1
    
    # Create new book entry
    new_book = pd.DataFrame({
        'id': [new_id],
        'title': [title],
        'author': [author],
        'genre': [genre],
        'owner': [owner],
        'price': [price],
        'publication_date': [publication_date]
    })
    
    # Append to existing books
    updated_books = pd.concat([books_df, new_book], ignore_index=True)
    updated_books.to_csv('data/books.csv', index=False)
    
    return new_id

def update_book(book_id, title, author, genre, owner, price, publication_date):
    """Update an existing book in the dataset."""
    books_df = get_books()
    
    if books_df.empty:
        return False
    
    # Find the book by ID
    book_index = books_df[books_df['id'] == book_id].index
    
    if len(book_index) == 0:
        return False
    
    # Update book details
    books_df.loc[book_index, 'title'] = title
    books_df.loc[book_index, 'author'] = author
    books_df.loc[book_index, 'genre'] = genre
    books_df.loc[book_index, 'owner'] = owner
    books_df.loc[book_index, 'price'] = price
    books_df.loc[book_index, 'publication_date'] = publication_date
    
    books_df.to_csv('data/books.csv', index=False)
    
    return True

def delete_book(book_id):
    """Delete a book from the dataset."""
    books_df = get_books()
    
    if books_df.empty:
        return False
    
    # Check if book exists
    if book_id not in books_df['id'].values:
        return False
    
    # Remove book
    books_df = books_df[books_df['id'] != book_id]
    books_df.to_csv('data/books.csv', index=False)
    
    # Remove associated sales
    sales_df = get_sales()
    if not sales_df.empty:
        sales_df = sales_df[sales_df['book_id'] != book_id]
        sales_df.to_csv('data/sales.csv', index=False)
    
    return True

def add_sale(book_id, date, quantity, price=None):
    """Add a new sale to the dataset."""
    sales_df = get_sales()
    books_df = get_books()
    
    # Check if book exists
    book = books_df[books_df['id'] == book_id]
    if book.empty:
        return False
    
    # If price is not provided, use the book's current price
    if price is None:
        price = book.iloc[0]['price']
    
    # Calculate revenue
    revenue = quantity * price
    
    # Create new sale entry
    new_sale = pd.DataFrame({
        'date': [date],
        'book_id': [book_id],
        'quantity': [quantity],
        'price': [price],
        'revenue': [revenue]
    })
    
    # Append to existing sales
    updated_sales = pd.concat([sales_df, new_sale], ignore_index=True)
    updated_sales.to_csv('data/sales.csv', index=False)
    
    return True

def delete_sale(index):
    """Delete a sale from the dataset."""
    sales_df = get_sales()
    
    if sales_df.empty or index >= len(sales_df):
        return False
    
    # Drop the sale by index
    sales_df = sales_df.drop(index)
    sales_df.to_csv('data/sales.csv', index=False)
    
    return True

def get_user_sales(username):
    """Get sales data for books owned by a specific user or all sales for admin."""
    sales_df = get_sales()
    books_df = get_books()
    
    if sales_df.empty or books_df.empty:
        return pd.DataFrame()
    
    # Merge sales with books to get book details
    merged_df = pd.merge(sales_df, books_df[['id', 'title', 'owner']], 
                         left_on='book_id', right_on='id')
    
    # If admin, return all sales, otherwise filter by owner
    if username == 'admin':
        return merged_df
    else:
        return merged_df[merged_df['owner'] == username]

def filter_sales_by_time_period(username, time_period):
    """Filter sales data by time period."""
    sales_df = get_user_sales(username)
    
    if sales_df.empty:
        return pd.DataFrame()
    
    # Convert date column to datetime
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    
    # Calculate date range based on time period
    today = datetime.now()
    
    if time_period == "Last 7 Days":
        start_date = today - timedelta(days=7)
    elif time_period == "Last 30 Days":
        start_date = today - timedelta(days=30)
    elif time_period == "Last 90 Days":
        start_date = today - timedelta(days=90)
    elif time_period == "Last Year":
        start_date = today - timedelta(days=365)
    else:  # All Time
        return sales_df
    
    # Filter by date range
    return sales_df[sales_df['date'] >= start_date]

def get_sales_trend(username, time_period):
    """Get sales trend data for visualization."""
    sales_df = filter_sales_by_time_period(username, time_period)
    
    if sales_df.empty:
        return pd.DataFrame(columns=['date', 'sales'])
    
    # Group by date and sum quantities
    sales_by_date = sales_df.groupby(sales_df['date'].dt.date)['quantity'].sum().reset_index()
    sales_by_date.columns = ['date', 'sales']
    
    # Sort by date
    sales_by_date = sales_by_date.sort_values('date')
    
    # Fill in missing dates with zero sales
    date_range = pd.date_range(
        start=sales_by_date['date'].min(),
        end=sales_by_date['date'].max()
    )
    
    full_date_df = pd.DataFrame({'date': date_range})
    full_date_df['date'] = full_date_df['date'].dt.date
    
    result = pd.merge(full_date_df, sales_by_date, on='date', how='left')
    result['sales'] = result['sales'].fillna(0)
    
    return result

def get_top_books(username, time_period, limit=5):
    """Get top selling books for the given time period."""
    sales_df = filter_sales_by_time_period(username, time_period)
    
    if sales_df.empty:
        return pd.DataFrame(columns=['title', 'sales'])
    
    # Group by book title and sum quantities
    top_books = sales_df.groupby('title')['quantity'].sum().reset_index()
    top_books.columns = ['title', 'sales']
    
    # Sort by sales in descending order and limit results
    top_books = top_books.sort_values('sales', ascending=False).head(limit)
    
    return top_books

def get_recent_sales(username, limit=10):
    """Get recent sales data."""
    sales_df = get_user_sales(username)
    
    if sales_df.empty:
        return pd.DataFrame()
    
    # Sort by date in descending order and limit results
    recent_sales = sales_df.sort_values('date', ascending=False).head(limit)
    
    return recent_sales

def get_sales_by_genre(username, time_period):
    """Get sales distribution by genre."""
    sales_df = filter_sales_by_time_period(username, time_period)
    books_df = get_books()
    
    if sales_df.empty or books_df.empty:
        return pd.DataFrame(columns=['genre', 'sales'])
    
    # Merge sales with books to get genre
    merged_df = pd.merge(sales_df, books_df[['id', 'genre']], 
                         left_on='book_id', right_on='id')
    
    # Group by genre and sum quantities
    sales_by_genre = merged_df.groupby('genre')['quantity'].sum().reset_index()
    sales_by_genre.columns = ['genre', 'sales']
    
    # Sort by sales in descending order
    sales_by_genre = sales_by_genre.sort_values('sales', ascending=False)
    
    return sales_by_genre

def get_users():
    """Get all users from the dataset."""
    if os.path.exists('data/users.csv'):
        users_df = pd.read_csv('data/users.csv')
        # Don't return password column for security
        if 'password' in users_df.columns:
            return users_df.drop(columns=['password'])
        return users_df
    return pd.DataFrame()

def get_clients():
    """Get all client users from the dataset."""
    users_df = get_users()
    
    if users_df.empty:
        return pd.DataFrame()
    
    return users_df[users_df['role'] == 'client']
