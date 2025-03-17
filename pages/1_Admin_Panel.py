import streamlit as st
import pandas as pd
from datetime import datetime
import data_manager
import auth

# Set page config
st.set_page_config(
    page_title="Admin Panel - Book Sales Tracker",
    page_icon="📚",
    layout="wide"
)

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please log in to access this page.")
    st.stop()

# Check if user is admin
if st.session_state.user_role != "admin":
    st.error("You don't have permission to access this page.")
    st.stop()

# Display user info in sidebar
auth.show_user_info()

# Main content
st.title("Admin Panel")

# Tabs for different admin functionalities
tab1, tab2, tab3 = st.tabs(["Book Management", "Sales Management", "User Management"])

with tab1:
    st.header("Book Management")
    
    # Book management section with two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Book")
        
        # Form for adding a new book
        with st.form("add_book_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            genre = st.selectbox(
                "Genre",
                ["Technology", "Business", "Marketing", "Science", "Fiction", "Non-Fiction", "Self-Help", "Other"]
            )
            
            # Get clients for owner selection
            clients = data_manager.get_clients()
            client_options = clients['username'].tolist() if not clients.empty else []
            
            owner = st.selectbox("Owner (Client)", client_options)
            isbn = st.text_input("ISBN", placeholder="e.g., 978-1-234567-89-0")
            royalty_percentage = st.number_input("Royalty Percentage (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
            price = st.number_input("Price ($)", min_value=0.0, max_value=1000.0, value=19.99, step=0.01)
            publication_date = st.date_input("Publication Date", value=datetime.now())
            
            submit_button = st.form_submit_button("Add Book")
            
            if submit_button:
                if not title or not author or not owner:
                    st.error("Please fill out all required fields.")
                else:
                    book_id = data_manager.add_book(
                        title=title,
                        author=author,
                        genre=genre,
                        owner=owner,
                        price=price,
                        publication_date=publication_date.strftime('%Y-%m-%d'),
                        isbn=isbn,
                        royalty_percentage=royalty_percentage
                    )
                    
                    if book_id:
                        st.success(f"Book '{title}' added successfully with ID: {book_id}")
                    else:
                        st.error("Failed to add book. Please try again.")
    
    with col2:
        st.subheader("Edit/Delete Books")
        
        # Get all books
        books_df = data_manager.get_books()
        
        if books_df.empty:
            st.info("No books available in the system.")
        else:
            # Select a book to edit
            book_titles = books_df['title'].tolist()
            book_titles.insert(0, "-- Select a book to edit --")
            selected_book_title = st.selectbox("Select Book", book_titles)
            
            if selected_book_title != "-- Select a book to edit --":
                # Get the selected book
                selected_book = books_df[books_df['title'] == selected_book_title].iloc[0]
                
                with st.form("edit_book_form"):
                    # Pre-fill form with current values
                    edit_title = st.text_input("Book Title", value=selected_book['title'])
                    edit_author = st.text_input("Author", value=selected_book['author'])
                    
                    genre_options = ["Technology", "Business", "Marketing", "Science", "Fiction", "Non-Fiction", "Self-Help", "Other"]
                    genre_index = genre_options.index(selected_book['genre']) if selected_book['genre'] in genre_options else 0
                    edit_genre = st.selectbox("Genre", genre_options, index=genre_index)
                    
                    # Get clients for owner selection
                    clients = data_manager.get_clients()
                    client_options = clients['username'].tolist() if not clients.empty else []
                    
                    # Find index of current owner in client options
                    owner_index = client_options.index(selected_book['owner']) if selected_book['owner'] in client_options else 0
                    edit_owner = st.selectbox("Owner (Client)", client_options, index=owner_index)
                    
                    # Get ISBN value if it exists
                    isbn_value = selected_book.get('isbn', '')
                    edit_isbn = st.text_input("ISBN", value=isbn_value, placeholder="e.g., 978-1-234567-89-0")
                    
                    # Get royalty percentage if it exists
                    royalty_value = selected_book.get('royalty_percentage', 10.0)
                    edit_royalty = st.number_input("Royalty Percentage (%)", min_value=0.0, max_value=100.0, value=float(royalty_value), step=0.5)
                    
                    edit_price = st.number_input("Price ($)", min_value=0.0, max_value=1000.0, value=float(selected_book['price']), step=0.01)
                    
                    # Parse the publication date
                    try:
                        pub_date = datetime.strptime(selected_book['publication_date'], '%Y-%m-%d')
                    except:
                        pub_date = datetime.now()
                    
                    edit_publication_date = st.date_input("Publication Date", value=pub_date)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button("Update Book")
                    with col2:
                        delete_button = st.form_submit_button("Delete Book", type="primary")
                    
                    if update_button:
                        if not edit_title or not edit_author or not edit_owner:
                            st.error("Please fill out all required fields.")
                        else:
                            success = data_manager.update_book(
                                book_id=selected_book['id'],
                                title=edit_title,
                                author=edit_author,
                                genre=edit_genre,
                                owner=edit_owner,
                                price=edit_price,
                                publication_date=edit_publication_date.strftime('%Y-%m-%d'),
                                isbn=edit_isbn,
                                royalty_percentage=edit_royalty
                            )
                            
                            if success:
                                st.success(f"Book '{edit_title}' updated successfully.")
                            else:
                                st.error("Failed to update book. Please try again.")
                    
                    if delete_button:
                        success = data_manager.delete_book(selected_book['id'])
                        
                        if success:
                            st.success(f"Book '{selected_book['title']}' deleted successfully.")
                            st.rerun()
                        else:
                            st.error("Failed to delete book. Please try again.")
    
    # Display all books
    st.subheader("All Books")
    books_df = data_manager.get_books()
    
    if not books_df.empty:
        # Display the books in a dataframe
        # Prepare column configuration
        column_config = {
            "id": "ID",
            "title": "Title",
            "author": "Author",
            "genre": "Genre",
            "owner": "Owner",
            "price": st.column_config.NumberColumn("Price", format="$%.2f"),
            "publication_date": "Publication Date"
        }
        
        # Add ISBN and royalty columns if they exist
        if 'isbn' in books_df.columns:
            column_config["isbn"] = "ISBN"
        
        if 'royalty_percentage' in books_df.columns:
            column_config["royalty_percentage"] = st.column_config.NumberColumn("Royalty %", format="%.1f%%")
            
        st.dataframe(
            books_df,
            use_container_width=True,
            column_config=column_config
        )
    else:
        st.info("No books available in the system.")

with tab2:
    st.header("Sales Management")
    
    # Sales management section with two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Add New Sale")
        
        # Form for adding a new sale
        with st.form("add_sale_form"):
            # Get all books for selection
            books_df = data_manager.get_books()
            
            if books_df.empty:
                st.info("No books available. Please add books first.")
                book_id = None
            else:
                book_options = [f"{row['id']} - {row['title']} ({row['owner']})" for _, row in books_df.iterrows()]
                selected_book = st.selectbox("Select Book", book_options)
                book_id = int(selected_book.split(' - ')[0]) if selected_book else None
            
            sale_date = st.date_input("Sale Date", value=datetime.now())
            quantity = st.number_input("Quantity Sold", min_value=1, max_value=1000, value=1, step=1)
            
            # Get current book price if a book is selected
            price = None
            if book_id is not None:
                book = books_df[books_df['id'] == book_id]
                if not book.empty:
                    price = book.iloc[0]['price']
                    st.info(f"Current book price: ${price:.2f}")
            
            # Option to override price
            override_price = st.checkbox("Override Price")
            if override_price:
                price = st.number_input("Sale Price ($)", min_value=0.0, max_value=1000.0, value=price if price else 19.99, step=0.01)
            
            submit_button = st.form_submit_button("Add Sale")
            
            if submit_button and book_id is not None:
                success = data_manager.add_sale(
                    book_id=book_id,
                    date=sale_date.strftime('%Y-%m-%d'),
                    quantity=quantity,
                    price=price if override_price else None
                )
                
                if success:
                    st.success(f"Sale added successfully!")
                else:
                    st.error("Failed to add sale. Please try again.")
    
    with col2:
        st.subheader("Recent Sales")
        
        # Get recent sales
        sales_df = data_manager.get_user_sales('admin')
        
        if sales_df.empty:
            st.info("No sales data available.")
        else:
            # Display the most recent sales
            recent_sales = sales_df.sort_values('date', ascending=False).head(10)
            
            st.dataframe(
                recent_sales[['date', 'title', 'quantity', 'price', 'revenue', 'owner']],
                use_container_width=True,
                column_config={
                    "date": "Date",
                    "title": "Book Title",
                    "quantity": "Quantity",
                    "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "owner": "Client"
                }
            )
    
    # Sales filtering and display
    st.subheader("Sales Data")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get clients for filtering
        clients = data_manager.get_clients()
        client_options = ['All Clients'] + clients['username'].tolist() if not clients.empty else ['All Clients']
        client_filter = st.selectbox("Filter by Client", client_options)
    
    with col2:
        # Get books for filtering
        books = data_manager.get_books()
        book_options = ['All Books'] + books['title'].tolist() if not books.empty else ['All Books']
        book_filter = st.selectbox("Filter by Book", book_options)
    
    with col3:
        # Date range filter
        date_filter = st.selectbox(
            "Filter by Date",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "Custom Range"]
        )
    
    # Custom date range
    if date_filter == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now())
    
    # Get and filter sales data
    sales_df = data_manager.get_user_sales('admin')
    
    if not sales_df.empty:
        # Apply client filter
        if client_filter != 'All Clients':
            sales_df = sales_df[sales_df['owner'] == client_filter]
        
        # Apply book filter
        if book_filter != 'All Books':
            sales_df = sales_df[sales_df['title'] == book_filter]
        
        # Apply date filter
        if date_filter != "All Time" and date_filter != "Custom Range":
            sales_df = data_manager.filter_sales_by_time_period('admin', date_filter)
        elif date_filter == "Custom Range":
            sales_df['date'] = pd.to_datetime(sales_df['date'])
            sales_df = sales_df[
                (sales_df['date'] >= pd.Timestamp(start_date)) & 
                (sales_df['date'] <= pd.Timestamp(end_date))
            ]
        
        # Display filtered sales data
        if not sales_df.empty:
            st.dataframe(
                sales_df[['date', 'title', 'quantity', 'price', 'revenue', 'owner']],
                use_container_width=True,
                column_config={
                    "date": "Date",
                    "title": "Book Title",
                    "quantity": "Quantity",
                    "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
                    "owner": "Client"
                }
            )
            
            # Display summary statistics
            total_sales = sales_df['quantity'].sum()
            total_revenue = sales_df['revenue'].sum()
            
            st.info(f"Total Books Sold: {total_sales} | Total Revenue: ${total_revenue:.2f}")
            
            # Export option
            if st.button("Export to CSV"):
                st.download_button(
                    label="Download Sales Data",
                    data=sales_df.to_csv(index=False).encode('utf-8'),
                    file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No sales data available for the selected filters.")

with tab3:
    st.header("User Management")
    
    # Create subtabs for User Management
    user_tabs = st.tabs(["All Users", "Add New User", "Edit User", "User Books"])
    
    with user_tabs[0]:
        # Get all users
        users_df = data_manager.get_users()
        
        if users_df.empty:
            st.info("No users available in the system.")
        else:
            # Display users in a dataframe
            st.dataframe(
                users_df,
                use_container_width=True,
                column_config={
                    "username": "Username",
                    "role": "Role",
                    "name": "Full Name",
                    "email": "Email"
                }
            )
    
    with user_tabs[1]:
        st.subheader("Add New User")
        
        # Form for adding a new user
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            new_role = st.selectbox("Role", ["client", "admin"])
            
            submit_button = st.form_submit_button("Add User")
            
            if submit_button:
                if not new_username or not new_password or not new_name:
                    st.error("Please fill out all required fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    # Call the add_user function from auth.py
                    import auth
                    success, message = auth.add_user(
                        username=new_username,
                        password=new_password,
                        name=new_name,
                        role=new_role,
                        email=new_email
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    with user_tabs[2]:
        st.subheader("Edit User")
        
        # Get all users for selection
        users_df = data_manager.get_users()
        
        if users_df.empty:
            st.info("No users available to edit.")
        else:
            # Select a user to edit
            usernames = users_df['username'].tolist()
            selected_username = st.selectbox("Select User to Edit", usernames)
            
            # Get selected user's current details
            selected_user = users_df[users_df['username'] == selected_username].iloc[0]
            
            # Edit user form
            with st.form("edit_user_form"):
                edit_name = st.text_input("Full Name", value=selected_user['name'])
                
                # Email field (may not exist in older records)
                edit_email = ""
                if 'email' in selected_user:
                    edit_email = st.text_input("Email", value=selected_user['email'])
                else:
                    edit_email = st.text_input("Email")
                
                edit_role = st.selectbox("Role", ["client", "admin"], index=0 if selected_user['role'] == "client" else 1)
                
                col1, col2 = st.columns(2)
                with col1:
                    update_button = st.form_submit_button("Update User")
                with col2:
                    delete_button = st.form_submit_button("Delete User")
                
                if update_button:
                    import auth
                    success, message = auth.update_user(
                        username=selected_username,
                        name=edit_name,
                        email=edit_email,
                        role=edit_role
                    )
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                
                if delete_button:
                    import auth
                    success, message = auth.delete_user(selected_username)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Change password section
            st.subheader("Change Password")
            
            with st.form("change_password_form"):
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                password_button = st.form_submit_button("Change Password")
                
                if password_button:
                    if not new_password:
                        st.error("Please enter a new password.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        import auth
                        success, message = auth.change_password(
                            username=selected_username,
                            new_password=new_password
                        )
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    with user_tabs[3]:
        st.subheader("User Books")
        
        # Get users with client role
        users_df = data_manager.get_users()
        client_options = users_df[users_df['role'] == 'client']['username'].tolist()
        
        if not client_options:
            st.info("No client users available.")
        else:
            # Select a user to view their books
            selected_client = st.selectbox("Select Client", client_options)
            
            if selected_client:
                client_books = data_manager.get_user_books(selected_client)
                
                if client_books.empty:
                    st.info(f"No books assigned to {selected_client}.")
                else:
                    st.dataframe(
                        client_books,
                        use_container_width=True,
                        column_config={
                            "id": "ID",
                            "title": "Title",
                            "author": "Author",
                            "genre": "Genre",
                            "price": st.column_config.NumberColumn("Price", format="$%.2f"),
                            "publication_date": "Publication Date"
                        }
                    )
                    
                    # User sales summary
                    user_sales = data_manager.get_user_sales(selected_client)
                    
                    if not user_sales.empty:
                        total_books_sold = user_sales['quantity'].sum()
                        total_revenue = user_sales['revenue'].sum()
                        
                        st.info(f"Total Books Sold: {total_books_sold} | Total Revenue: ${total_revenue:.2f}")
