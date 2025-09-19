import db
from collections import Counter
from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request, current_app

routes_bp = Blueprint('routes_bp', __name__, url_prefix='/api/v1')

# Required Endpoints
@routes_bp.route('/books', methods=['GET'])
def get_all_books():
  """
  List all books.
  Returns a list of all books in the database.
  ---
  tags:
    - Required Endpoints
  responses:
    200:
      description: List all books.
      schema:
        type: array
        items:
          type: object
          properties:
            id:
              type: integer
            Title:
              type: string
            Rating:
              type: string
            Price:
              type: string
            Image:
              type: string
            Category:
              type: string
            Availability:
              type: string
    500:
      description: Data not available or failed to load.
      schema:
        type: object
        properties:
          msg:
            type: string
  """
  try:
    conn = db.get_db()
    books = conn.execute('SELECT * FROM books ORDER BY title').fetchall()
    books_dict = [dict(book) for book in books]
    return jsonify(books_dict)
  except Exception as e:
    print(f"Error fetching all books: {e}")
    return jsonify({'msg': 'Data not available or failed to load.'}), 500

@routes_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
  """
  Get a book by ID.
  Returns details of a book by ID.
  ---
  tags:
    - Required Endpoints
  parameters:
    - name: book_id
      in: path
      required: true
      schema:
        type: integer
        format: int64
        example: 1
  responses:
    200:
      description: Returns details of a book by ID.
      schema:
        type: object
        properties:
          id:
            type: integer
          Title:
            type: string
          Rating:
            type: string
          Price:
            type: string
          Image:
            type: string
          Category:
            type: string
          Availability:
            type: string
    404:
      description: Book Not Found.
      schema:
        type: object
        properties:
          msg:
            type: string
    500:
      description: Data not available or failed to load.
      schema:
        type: object
        properties:
          msg:
            type: string
  """
  try:
      conn = db.get_db()
      book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
      if book is None:
        return jsonify({'msg': 'Book Not Found.'}), 404
      return jsonify(dict(book))
  except Exception as e:
      print(f"Error fetching book by ID: {e}")
      return jsonify({'msg': 'Data not available or failed to load.'}), 500

@routes_bp.route('/books/search', methods=['GET'])
def search_books():
  """
  Search books by title and/or category.
  Returns a list of books matching the search criteria.
  ---
  tags:
    - Required Endpoints
  parameters:
    - name: title
      in: query
      required: false
      schema:
        type: string
      example: "Street"
    - name: category
      in: query
      required: false
      schema:
        type: string
      example: "Mystery"
  responses:
    200:
      description: Returns a list of books matching the search criteria.
      schema:
        type: array
        items:
          type: object
          properties:
            id:
              type: integer
            Title:
              type: string
            Rating:
              type: string
            Price:
              type: string
            Image:
              type: string
            Category:
              type: string
            Availability:
              type: string
    503:
      description: Data not available or failed to load.
      schema:
        type: object
        properties:
          msg:
            type: string
  """ 
  try:
    query_title = request.args.get('title', type=str)
    query_category = request.args.get('category', type=str)
    query = 'SELECT * FROM books WHERE 1=1'
    params = []
    if query_title:
      query += ' AND upper(title) LIKE ?'
      params.append(f'%{query_title.upper()}%')
    if query_category:
      query += ' AND upper(category) = ?'
      params.append(query_category.upper())
    # print(f"Executing query: {query} with params: {params}")
    conn = db.get_db()
    books = conn.execute(query, params).fetchall()
    books_dict = [dict(book) for book in books]
    return jsonify(books_dict)
  except Exception as e:
    print(f"Error searching books: {e}")
    return jsonify({'msg': 'Data not available or failed to load.'}), 500

@routes_bp.route('/categories', methods=['GET'])
def get_all_categories():
  """
  Get all categories.
  Returns a list of all unique book categories.
  ---
  tags:
    - Required Endpoints
  responses:
    200:
      description: Returns a list of all unique book categories.
      schema:
        type: object
        properties:
          categories:
            type: array
            items:
              type: string
    503:
      description: Data not available or failed to load.
      schema:
        type: object
        properties:
          msg:
            type: string
  """ 
  try:
    conn = db.get_db()
    categories = conn.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
    categories_list =[row['category'] for row in categories]
    return jsonify({'categories': categories_list})
  except Exception as e:
    print(f"Error fetching categories: {e}")
    return jsonify({'msg': 'Data not available or failed to load.'}), 500

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