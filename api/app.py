import os
import csv
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- Carregamento de Dados ---
def load_books_data():
    """
    Carrega os dados do arquivo CSV e adiciona um ID único para cada livro.
    Esta função é chamada uma vez quando o servidor inicia.
    """
    data_path = os.path.join('data', 'scraped_books.csv')
    if not os.path.exists(data_path):
        # Retorna uma lista vazia e uma flag de erro se o arquivo não existir
        return [], False 
    
    books = []
    try:
        with open(data_path, mode='r', encoding='utf-8') as csv_file:
            # DictReader lê cada linha como um dicionário
            csv_reader = csv.DictReader(csv_file)
            # Adiciona um ID sequencial a cada livro
            for i, row in enumerate(csv_reader):
                row['id'] = i + 1
                books.append(row)
        return books, True
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return [], False

# Carrega os dados na inicialização da API
BOOKS_DATA, DATA_LOADED_SUCCESSFULLY = load_books_data()

# --- Definição dos Endpoints da API ---

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificação de status da API e conectividade com os dados.
    """
    if DATA_LOADED_SUCCESSFULLY:
        return jsonify({
            "status": "ok",
            "message": "API está funcional e os dados foram carregados com sucesso.",
            "book_count": len(BOOKS_DATA)
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "API está funcional, mas falhou ao carregar os dados do arquivo CSV.",
            "data_source": "data/livros_extraidos.csv"
        }), 503 # Service Unavailable


@app.route('/api/v1/books', methods=['GET'])
def get_all_books():
    """
    Lista todos os livros disponíveis na base de dados.
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({"error": "Dados não disponíveis"}), 503
        
    return jsonify(BOOKS_DATA)


@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """
    Retorna detalhes completos de um livro específico pelo ID.
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({"error": "Dados não disponíveis"}), 503

    # Procura o livro na lista pelo ID
    book = next((book for book in BOOKS_DATA if book['id'] == book_id), None)
    
    if book:
        return jsonify(book)
    else:
        # Retorna 404 Not Found se o livro não for encontrado
        return jsonify({"error": "Livro não encontrado"}), 404


@app.route('/api/v1/categories', methods=['GET'])
def get_all_categories():
    """
    Lista todas as categorias de livros disponíveis, sem duplicatas.
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({"error": "Dados não disponíveis"}), 503

    # Usa um set para extrair categorias únicas e depois converte para lista
    categories = sorted(list(set(book['Categoria'] for book in BOOKS_DATA)))
    return jsonify({"categories": categories})


@app.route('/api/v1/books/search', methods=['GET'])
def search_books():
    """
    Busca livros por título e/ou categoria usando query parameters.
    Ex: /api/v1/books/search?title=secret&category=mystery
    """
    if not DATA_LOADED_SUCCESSFULLY:
        return jsonify({"error": "Dados não disponíveis"}), 503

    # Pega os argumentos da URL
    query_title = request.args.get('title', type=str)
    query_category = request.args.get('category', type=str)

    # Começa com a lista completa de livros
    results = BOOKS_DATA

    # Filtra por título (busca case-insensitive se o parâmetro for fornecido)
    if query_title:
        results = [book for book in results if query_title.lower() in book['Título'].lower()]

    # Filtra por categoria (busca case-insensitive se o parâmetro for fornecido)
    if query_category:
        results = [book for book in results if query_category.lower() == book['Categoria'].lower()]
        
    return jsonify(results)


# Ponto de entrada para executar a aplicação
if __name__ == '__main__':
    # O modo debug reinicia o servidor automaticamente após alterações no código.
    # Em produção, use um servidor WSGI como Gunicorn ou uWSGI.
    app.run(debug=True, port=5000)
