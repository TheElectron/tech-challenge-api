from . import db
import threading
from scripts import scraper
from flask_jwt_extended import jwt_required
from flask import Blueprint, jsonify, request, render_template

routes_bp = Blueprint('routes_bp', __name__, url_prefix='/api/v1')

@routes_bp.route('/', methods=['GET'])
def index():
  return render_template('index.html')

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
@routes_bp.route('/stats/overview', methods=['GET'])
def get_stats_overview():
  """
  Get books overview.
  Returns total number of books, average price, and ratings distribution.
  ---
  tags:
    - Optional Endpoints
  responses:
    200:
      description: Returns total number of books, average price, and ratings distribution.
      schema:
        type: object
        properties:
          total_books:
            type: integer
          average_price:
            type: string
          ratings_distribution:
            type: object
            properties:
              1 estrela(s):
                type: integer
              2 estrela(s):
                type: integer
              3 estrela(s):
                type: integer
              4 estrela(s):
                type: integer
              5 estrela(s):
                type: integer
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
    query = """
              SELECT 
                COUNT(id) as total_books, 
                AVG(price) as average_price 
                FROM books
            """
    geral_stats = conn.execute(query).fetchone()
    query = """
              SELECT 
                rating, 
                COUNT(id) as count 
              FROM books 
              GROUP BY rating 
              ORDER BY rating
            """
    ratings_stats = conn.execute(query).fetchall()
    ratings_distribution = {f"{row['rating']} estrela(s)": row['count'] for row in ratings_stats}
    response = {
        "total_books": geral_stats['total_books'],
        "average_price": f"£{round(geral_stats['average_price'], 2) if geral_stats['average_price'] else 0}",
        "ratings_distribution": ratings_distribution
    }        
    return jsonify(response), 200
  except Exception as e:
    print(f"Error fetching books stats overview: {e}")
    return jsonify({'msg': 'Data not available or failed to load.'}), 500

@routes_bp.route('/stats/categories', methods=['GET'])
def get_stats_categories():
  """
  Get stats by category.
  Returns number of books and average price per category.
  ---
  tags:
    - Optional Endpoints
  responses:
    200:
      description: Returns number of books and average price per category.
      schema:
        type: object
        properties:
          category_name:
            type: object
            properties:
              books:
                type: integer
              average_price:
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
    query = """
              SELECT
                  category,
                  COUNT(id) as book_count,
                  AVG(price) as average_price
              FROM books
              GROUP BY category
              ORDER BY category
            """
    stats_rows = conn.execute(query).fetchall()
    category_stats = {}
    for row in stats_rows:
        category_stats[row['category']] = {
            "books": row['book_count'],
            "average_price": f"£{round(row['average_price'], 2)}"
        }
    return jsonify(category_stats)
  except Exception as e:
      print(f"Error fetching books stats by category: {e}")
      return jsonify({'msg': 'Data not available or failed to load.'}), 500

@routes_bp.route('/books/top-rated', methods=['GET'])
def get_top_rated_books():
  """
  Get details of top rating books.
  Returns a list of books with a 5-star rating.
  ---
  tags:
    - Optional Endpoints
  responses:
    200:
      description: Returns a list of books with a 5-star rating.
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
    conn = db.get_db()
    query = """
          SELECT *
          FROM books
          WHERE rating = '5'
          ORDER BY title
        """
    top_rated_books = conn.execute(query).fetchall()
    top_rated_books_dict = [dict(book) for book in top_rated_books]
    return jsonify(top_rated_books_dict) # OK
  except Exception as e:
      print(f"Error fetching top rated books: {e}")
      return jsonify({'msg': 'Data not available or failed to load.'}), 500

@routes_bp.route('/books/price-range', methods=['GET'])
def get_books_by_price_range():
  """
  Filtra livros dentro de uma faixa de preço específica.
  Returns a list of books within a specified price range.
  ---
  tags:
    - Optional Endpoints
  responses:
    200:
      description: Returns a list of books within a specified price range.
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
    400:
      description: Data not available or failed to load.
      schema:
        type: object
        properties:
          msg:
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
    min_price = request.args.get('min', default=0, type=float)
    max_price = request.args.get('max', default=float('inf'), type=float)
    if min_price < 0 or max_price < 0:
      return jsonify({"msg": "Preços mínimo e máximo não podem ser negativos."}), 400
    if min_price > max_price:
      return jsonify({"msg": "O preço mínimo não pode ser maior que o preço máximo."}), 400
    conn = db.get_db()
    query = """
          SELECT *
          FROM books
          WHERE price BETWEEN ? AND ?
          ORDER BY title
        """
    books_in_range = conn.execute(query, (min_price, max_price)).fetchall()
    books_list = [dict(book) for book in books_in_range]
    return jsonify(books_list) # OK
  except Exception as e:
    print(f"Error fetching price range: {e}")
    return jsonify({'msg': 'Data not available or failed to load.'}), 500

# Web Scraping Endpoint
@routes_bp.route('/scraping/trigger', methods=['POST'])
@jwt_required()
def trigger_scrape():
  """
  Inicia o processo de web scraping em segundo plano.
  Não espera o processo terminar e retorna uma resposta imediata.
  """
  # Verifica se já existe um processo de scraping rodando antes de iniciar outro
  active_threads = [t.name for t in threading.enumerate()]
  if 'scraping_thread' in active_threads:
    return jsonify({"msg": "A scraping process is already running."}), 409
  # Cria uma thread para executar a função de scraping
  scrape_thread = threading.Thread(target=scraper.run_scraping_process, name='scraping_thread')
  # Inicia a execução da thread em segundo plano
  scrape_thread.start()
  return jsonify({"status": "accepted", "msg": "The scraping process has started."}), 202
