import os
import csv
from flasgger import Swagger
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from . import db
from .auth import auth_bp
from .routes import routes_bp

def load_books_data():
    """
        Loads the file 'scraped_books.csv' and adds an ID for each book.
        Returns a tuple (books, success) where 'books' is a list of dictionaries.
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

def create_app():
    """
        Initializes the Flask application, loads configurations, and registers blueprints.
    """
    app = Flask(__name__)
    load_dotenv()
    # Auth Config
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    jwt = JWTManager(app)
    # Flasgger Config
    app.config['SWAGGER'] = {
        'title': 'Books API',
        'version': '1.0',
        'description': 'Uma API para consultar dados de livros extraídos por web scraping.',
        'uiversion': 3,
        'securityDefinitions': { # Define o esquema de segurança para JWT
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Token de acesso JWT. Formato: "Bearer <token>"'
            }
        },
        'security': [{'Bearer': []}] # Aplica a segurança JWT a todos os endpoints por padrão
    }
    swagger = Swagger(app)
    # Database Config
    app.config['DATABASE_PATH'] = os.path.join('data', 'tech_challenge_api.db')
    db.init_app(app)
    # Blueprints for routes and authentication
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    # Health check endpoint
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        try:
            conn = db.get_db()
            conn.execute('SELECT * FROM books LIMIT 1')
            return jsonify({
                "status": "OK", 
                "message": "API is functional and database is accessible!"
            }), 200
        except Exception as e:
            return jsonify({
                "status": "ERROR", 
                "message": "Failed on health check"
            }), 503
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=8000)
