from flask import Flask, jsonify, render_template, request
import sqlite3

app = Flask(__name__)

# Define the path to your SQLite database file
DATABASE = 'db/books.db'

@app.route('/api/books', methods=['GET'])
def get_all_books():
    try:
        print('Getting all books...')
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Fetch all authors
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        author_dict = {author[0]: author[1] for author in authors}

        # Fetch books with author names
        cursor.execute("SELECT Books.book_id, Books.title, Books.publication_year, GROUP_CONCAT(Authors.name, ', ') AS author_names "
                       "FROM Books "
                       "LEFT JOIN book_author ON Books.book_id = book_author.book_id "
                       "LEFT JOIN Authors ON book_author.author_id = Authors.author_id "
                       "GROUP BY Books.book_id, Books.title, Books.publication_year")
        books = cursor.fetchall()
        conn.close()

        # Convert the list of tuples into a dictionary of books
        book_dict = {}
        for book in books:
            book_id = book[0]
            title = book[1]
            publication_year = book[2]
            author_name = book[3]

            if book_id not in book_dict:
                book_dict[book_id] = {
                    'book_id': book_id,
                    'title': title,
                    'publication_year': publication_year,
                    'authors': []  # Initialize list of authors
                }

            if author_name:
                book_dict[book_id]['authors'].append(author_name)

        book_list = list(book_dict.values())

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)})


# API to get all authors
@app.route('/api/authors', methods=['GET'])
def get_all_authors():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        conn.close()
        return jsonify(authors)
    except Exception as e:
        return jsonify({'error': str(e)})

# API to get all reviews
@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reviews")
        reviews = cursor.fetchall()
        conn.close()
        return jsonify(reviews)
    except Exception as e:
        return jsonify({'error': str(e)})

# API to add a book to the database
@app.route('/api/add_book', methods=['POST'])
def add_book():
    try:
        print('Add a new book...')
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Get book details from the request
        data = request.get_json()
        title = data.get('title')
        publication_year = data.get('publication_year')
        author_names = data.get('author_name')
        author_list = [name.strip() for name in author_names.split(',')]

        # Insert the book into the database
        cursor.execute("INSERT INTO Books (title, publication_year) VALUES (?, ?)", (title, publication_year))
        book_id = cursor.lastrowid

        for author_name in author_list:
            # adds the author to the already existing authors table if the author does not exist yet, then grabs the ID of that author being added so it can be matched
            cursor.execute("INSERT OR IGNORE INTO Authors (name) VALUES (?)", (author_name,))
            cursor.execute("SELECT author_id FROM Authors WHERE name=?", (author_name,))
            author_id = cursor.fetchone()[0]

            # Insert the book-author relationship into book_author table
            cursor.execute("INSERT INTO book_author (book_id, author_id) VALUES (?, ?)", (book_id, author_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
