# This file bla bla ...

import os
import csv
from flask import Flask, jsonify
from datetime import timedelta
from dotenv import load_dotenv

from flask_jwt_extended import JWTManager

from auth import auth_bp
from routes import routes_bp

def load_books_data():
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
    # Data Loading
    books_data, success = load_books_data()
    app.config['BOOKS_DATA'] = books_data
    app.config['DATA_LOADED_SUCCESSFULLY'] = success
    if not success:
        print("ALERTA: Falha crítica ao carregar os dados dos livros.") # Traduzir essa merda?
    # Blueprints for routes and authentication
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    # Health check endpoint
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        if app.config['DATA_LOADED_SUCCESSFULLY']:
            return jsonify({"status": "ok", "message": "API está funcional e os dados foram carregados."}), 200
        else:
            return jsonify({"status": "error", "message": "API funcional, mas dados não carregados."}), 503
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
