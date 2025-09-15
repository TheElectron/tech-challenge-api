# This file contains the routes for the Flask application.

from flask import Blueprint, jsonify, request, current_app
from collections import Counter
from flask_jwt_extended import jwt_required

routes_bp = Blueprint('routes_bp', __name__, url_prefix='/api/v1')

# Check if books data has been loaded
def check_data_loaded():
    return current_app.config.get('DATA_LOADED_SUCCESSFULLY', False)

@routes_bp.before_request
def before_request_func():
    # This hook runs before every request in this blueprint
    # If the data was not loaded, return an error for any route
    if not check_data_loaded():
        return jsonify({
            "status": "error",
            "message": "Erro ao carregar livro."
        }), 503 # Service Unavailable    

# Required Endpoints
@routes_bp.route('/books', methods=['GET'])
def get_all_books():
    """
        List all books.
    """
    return jsonify(current_app.config['BOOKS_DATA'])

@routes_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """
        Returns details of a book by ID.
    """
    book = next((book for book in current_app.config['BOOKS_DATA'] if book['id'] == book_id), None)
    if book:
        return jsonify(book)
    else:
        return jsonify({
                "status": "error",
                "message": "Livro não encontrado."
            }), 404 # Not Found

@routes_bp.route('/api/v1/books/search', methods=['GET'])
def search_books():
    """
        Search for books by title and/or category using query parameters.
        Ex: /api/v1/books/search?title=secret&category=mystery
    """ 
    # Get query parameters
    query_title = request.args.get('title', type=str)
    query_category = request.args.get('category', type=str)
    results = current_app.config['BOOKS_DATA']
    # Filter by category
    if query_category:
        results = [book for book in results if query_category.lower() == book['Category'].lower()]
    # Filter by title
    if query_title:
        results = [book for book in results if query_title.lower() in book['Title'].lower()]
    return jsonify(results)

@routes_bp.route('/categories', methods=['GET'])
def get_all_categories():
    categories = sorted(list(set(book['Category'] for book in current_app.config['BOOKS_DATA'])))
    return jsonify({"categories": categories})

# Optional Endpoints
@routes_bp.route('/api/v1/stats/overview', methods=['GET'])
def get_stats_overview():
    """
        Get books overview.
    """
    total_books = len(current_app.config['BOOKS_DATA'])
    total_price = sum(float(book['Price']) for book in current_app.config['BOOKS_DATA'])
    average_price = round(total_price / total_books, 2)
    ratings_distribution = Counter(book['Rating'] for book in current_app.config['BOOKS_DATA'])
    ratings = {f"{stars} estrela(s)": count for stars, count in sorted(ratings_distribution.items())}
    return jsonify({
        "total_books": total_books,
        "average_price": f"£{average_price}",
        "ratings_distribution": ratings
    }), 200 # OK

@routes_bp.route('/api/v1/stats/categories', methods=['GET'])
def get_stats_categories():
    """
        Get stats by category.
    """
    category_stats = {}
    categories = set(book['Category'] for book in current_app.config['BOOKS_DATA'])
    for category in categories:
        books_in_category = [b for b in current_app.config['BOOKS_DATA'] if b['Category'] == category]
        count = len(books_in_category)
        if count > 0:
            avg_price = round(sum(float(book['Price']) for book in books_in_category) / count, 2)
        else:
            avg_price = 0
        category_stats[category] = {
            "books": count,
            "average_price": f"£{avg_price}"
        }
    return jsonify(dict(sorted(category_stats.items()))) # OK

@routes_bp.route('/api/v1/books/top-rated', methods=['GET'])
def get_top_rated_books():
    """
        Get details of top rating books.
    """
    top_rated_books = [book for book in current_app.config['BOOKS_DATA'] if book['Rating'] == '5']
    return jsonify(top_rated_books) # OK

@routes_bp.route('/api/v1/books/price-range', methods=['GET'])
def get_books_by_price_range():
    """
    Filtra livros dentro de uma faixa de preço específica.
    Ex: /api/v1/books/price-range?min=10&max=20
    """
    try:
        min_price = request.args.get('min', default=0, type=float)
        max_price = request.args.get('max', default=float('inf'), type=float)
    except ValueError:
        return jsonify({
            "error": "error",
            "message": "Parâmetros inválidos."}), 400 # Bad Request
    filtered_books = [book for book in current_app.config['BOOKS_DATA'] if min_price <= float(book['Price']) <= max_price]
    return jsonify(filtered_books)