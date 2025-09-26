import os
import sqlite3
from scripts import scraper
from flask import current_app, g

def get_db():
    """
    Cria e retorna uma conexão com o banco de dados para a requisição atual.
    A conexão é armazenada no objeto 'g' do Flask, que é único para cada requisição.
    """
    if 'db' not in g:
        db_path = current_app.config['DATABASE_PATH']
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found at: {db_path}.")     
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Fecha a conexão com o banco de dados ao final da requisição."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """
    Registra a função de fechamento do banco de dados com a aplicação Flask.
    Isso garante que close_db() seja chamada após cada requisição.
    """
    scraper.run_scraping_process()
    app.teardown_appcontext(close_db)
