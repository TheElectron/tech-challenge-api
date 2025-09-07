import os
import csv
from flask import Flask, jsonify, request

def load_data():
    """
        Loads the file 'scraped_books.csv' and adds an ID for each book.
    """
    data_path = os.path.join('data', 'scraped_books.csv')
    if not os.path.exists(data_path):
        return [], False 
    books = []
    try:
        with open(data_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for i, row in enumerate(csv_reader):
                row['id'] = i + 1
                books.append(row) # Adds a sequential ID to each book
        return books, True
    except Exception as e:
        print(f"Error loading .csv file: {e}")
        return [], False

# Load data at API initialization
BOOKS_DATA, DATA_LOADED_SUCCESSFULLY = load_data()
app = Flask(__name__)

@app.route('/api/v1/books', methods=['GET'])
def get_all_books():
    """
        List all books.
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({
            "status": "error",
            "message": "Erro ao carregar os dados."
        }), 503 # Service Unavailable    
    return jsonify(BOOKS_DATA)

@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """
        Returns details of a book by ID.
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({
            "status": "error",
            "message": "Erro ao carregar livro."
        }), 503 # Service Unavailable    
    book = next((book for book in BOOKS_DATA if book['id'] == book_id), None)
    if book:
        return jsonify(book)
    else:
        return jsonify({
            "status": "error",
            "message": "Livro não encontrado."
        }), 404 # Not Found

@app.route('/api/v1/books/search', methods=['GET'])
def search_books():
    """
        Search for books by title and/or category using query parameters.
        Ex: /api/v1/books/search?title=secret&category=mystery
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({
            "status": "error",
            "message": "Erro ao carregar livro."
        }), 503 # Service Unavailable    
    # Get query parameters
    query_title = request.args.get('title', type=str)
    query_category = request.args.get('category', type=str)
    results = BOOKS_DATA
    # Filter by category
    if query_category:
        results = [book for book in results if query_category.lower() == book['Category'].lower()]
    # Filter by title
    if query_title:
        results = [book for book in results if query_title.lower() in book['Title'].lower()]
    return jsonify(results)

@app.route('/api/v1/categories', methods=['GET'])
def get_all_categories():
    """
        Lists all book categories.
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({
            "error": "error",
            "message": "Erro ao listar categorias."
        }), 503 # Service Unavailable
    categories = sorted(list(set(book['Category'] for book in BOOKS_DATA)))
    return jsonify({"categories": categories})

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """
        Health Check Endpoint is responsible for checking API status and data connectivity.
    """
    if DATA_LOADED_SUCCESSFULLY:
        return jsonify({
            "status": "ok",
            "message": "API está funcional e os dados foram carregados com sucesso.",
            "book_count": len(BOOKS_DATA)
        }), 200 # OK
    else:
        return jsonify({
            "status": "error",
            "message": "API está funcional, mas falhou ao carregar os dados do arquivo CSV.",
        }), 503 # Service Unavailable

if __name__ == '__main__':
    # O modo debug reinicia o servidor automaticamente após alterações no código.
    # Em produção, use um servidor WSGI como Gunicorn ou uWSGI.
    app.run(debug=True, port=5000)
