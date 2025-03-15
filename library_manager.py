import json
import streamlit as st
import pandas as pd
import time
from datetime import datetime

# File to store books
db_file = "books_data.json"

# Load books from file
def load_books():
    try:
        with open(db_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save books to file
def save_books(books):
    with open(db_file, "w") as file:
        json.dump(books, file, indent=4)

# Load book collection
books = load_books()

# Streamlit UI Styling
st.set_page_config(page_title="📚 Personal Library Manager", layout="centered")
st.markdown(
    """
    <style>
        .main {background-color: #f4f4f4; text-align: center;}
        div[data-testid="stSidebar"] {background-color: #2e3b4e; color: white;}
        h1, h2, h3 {color: #2e3b4e; text-align: center;}
        .stButton>button {width: 100%; background-color: #2e3b4e; color: white;}
        .stDataFrame {margin: auto;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Navigation at the top
st.title("📚 Personal Library Manager")
menu = st.radio("Select an Option", ["Add Book", "View Books", "Statistics", "Manage Books"], horizontal=True)

if menu == "Add Book":
    st.subheader("📖 Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title").strip()
        author = st.text_input("Author").strip()
        year = st.number_input("Publication Year", min_value=0, max_value=2025, step=1)
        genre = st.text_input("Genre").strip()
        read_status = st.checkbox("Mark as Read")
        submitted = st.form_submit_button("➕ Add Book")

        if submitted:
            if title and author and genre:
                if any(book["title"].lower() == title.lower() for book in books):
                    st.error("⚠️ This book already exists!")
                else:
                    new_book = {
                        "title": title,
                        "author": author,
                        "year": year,
                        "genre": genre,
                        "read": read_status,
                        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    books.append(new_book)
                    save_books(books)
                    st.success("✅ Book added successfully!")
                    time.sleep(1)  # Delay for 5 seconds
                    st.rerun()
            else:
                st.error("⚠️ Please fill in all required fields!")

elif menu == "View Books":
    st.subheader("📚 Your Book Collection")
    df = pd.DataFrame(books)
    
    if not df.empty:
        search_query = st.text_input("🔍 Search by Title or Author").strip().lower()
        if search_query:
            df = df[df["title"].str.lower().str.contains(search_query, na=False) | 
                    df["author"].str.lower().str.contains(search_query, na=False)]
        
        st.dataframe(df.style.set_properties(**{"background-color": "#f4f4f4", "color": "black"}), use_container_width=True)
    else:
        st.warning("⚠️ No books found. Add some!")

elif menu == "Statistics":
    st.subheader("📊 Library Statistics")
    total_books = len(books)
    read_books = sum(1 for book in books if book.get("read", False))
    unread_books = total_books - read_books
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
    
    st.metric("Total Books", total_books)
    st.metric("Books Read", read_books, "📖")
    st.metric("Books Unread", unread_books, "📕")
    st.metric("Reading Progress", f"{read_percentage:.2f}%", "📊")

elif menu == "Manage Books":
    st.subheader("🛠 Manage Your Books")
    df = pd.DataFrame(books)
    
    if not df.empty:
        selected_title = st.selectbox("Select a Book to Edit or Delete", df["title"].tolist())
        book_to_edit = next((book for book in books if book["title"] == selected_title), None)
        
        if book_to_edit:
            with st.form("edit_book_form"):
                new_title = st.text_input("Title", book_to_edit["title"]).strip()
                new_author = st.text_input("Author", book_to_edit["author"]).strip()
                new_year = st.number_input("Publication Year", min_value=0, max_value=2025, step=1, value=int(book_to_edit["year"]))
                new_genre = st.text_input("Genre", book_to_edit["genre"]).strip()
                new_read_status = st.checkbox("Mark as Read", book_to_edit["read"])
                update_submitted = st.form_submit_button("✅ Update Book")

                if update_submitted:
                    if new_title and new_author and new_genre:
                        book_to_edit.update({
                            "title": new_title,
                            "author": new_author,
                            "year": new_year,
                            "genre": new_genre,
                            "read": new_read_status
                        })
                        save_books(books)
                        st.success("✔ Book updated successfully!")
                        time.sleep(1)  # Delay for 5 seconds
                        st.rerun()
                    else:
                        st.error("⚠️ Please fill in all required fields!")

            if st.button("❌ Delete Book", key="delete_book"):
                books.remove(book_to_edit)
                save_books(books)
                st.warning("⚠ Book deleted!")
                time.sleep(1)  # Delay for 5 seconds
                st.rerun()
    else:
        st.warning("⚠ No books found.")
