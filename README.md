# Tech Challenge #01 |  API de Livros 📖

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.x-black.svg)
![Gunicorn](https://img.shields.io/badge/gunicorn-21.x-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

## 💻 Descrição do Projeto

Este projeto foi desenvolvido para o **Tech Challenge #01** da Pós-Graduação em  **Machine Learning Engineering** da FIAP.

Seu objetivo é demonstrar um pipeline de dados *end to end*, desde a extração de dados do site [books.toscrape.com](http://books.toscrape.com/) utilizando web scraping, até sua exposição através de uma API.  

Abordando desde a coleta e armazenamento dos dados até o tratamento e disponibilização para consumo.

## ⭐ Tecnologias Utilizadas
* **Backend**: Python 3.10+, Flask
* **Servidor WSGI**: Gunicorn
* **Banco de Dados**: SQLite
* **Web Scraping**: Requests, BeautifulSoup4
* **Documentação da API**: Flasgger (Swagger UI)
* **Autenticação**: JWT (JSON Web Tokens) com `Flask-JWT-Extended`
* **Variáveis de Ambiente**: `python-dotenv`

## 🏢 Arquitetura

A arquitetura da aplicação é composta por três componentes principais:
1.  **Web Scraper**: Um script Python (`scripts/scraper.py`) que navega pelo site [books.toscrape.com](http://books.toscrape.com/), extrai informações detalhadas de cada livro e as armazena no banco de dados.

2.  **Banco de Dados**: Um banco de dados **SQLite** (`data/livros.db`) que serve como fonte única de dados dos livros.

3.  **API**: O servidor **Flask** (`api/`) que expõe uma série de endpoints para consultar os dados do banco.

![Nome da imagem](tech.svg)

## ⚙️ Instalação e Configuração

### Pré-requisitos
* Python 3.10 ou superior
* Gerenciador de pacotes do Python (*pip*)
* Git

### Instruções para instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/TheElectron/tech-challenge-api.git
    cd tech-challenge-api
    ```

2.  **Crie e ative um ambiente virtual:**  
* No Windows:  
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

* No macOS/Linux:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ``` 
    

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**  
    Crie um arquivo chamado `.env` na raiz do projeto e adicione a chave secreta para o JWT.
    ```
    JWT_SECRET_KEY='seu_valor_secreto_e_dificil_de_adivinhar_aqui'
    ```

    Você pode usar o comando para gerar a chave privada.
    ```bash
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

5. **Execução:**  
    Para executar a API usando o Gunicorn:
    ```bash
    gunicorn --config gunicorn.conf.py "api.app:create_app()"
    ```

    A API estará disponível em http://127.0.0.1:8000/api/v1/.  
    Você também pode interagir com a versão disponivel online,
    em https://tech-challenge-api-vjl1.onrender.com/api/v1/.

## 📖 Documentação das Rotas

### Documentação Interativa (Swagger UI)

A fonte primária documentação para esta API é a interface interativa do Swagger, gerada automaticamente pelo Flasgger. 

Através dela, é possível ver todos os endpoints em detalhe, seus parâmetros, schemas de request/response e, mais importante, **executar chamadas de teste em tempo real** diretamente do seu navegador.

### Resumo dos Endpoints

A tabela abaixo fornece um resumo rápido dos principais endpoints disponíveis. Para detalhes completos, consulte a documentação interativa.

| Método | Endpoint | Descrição | Autenticação |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Retorna a página inicial de boas-vindas da API (HTML). | Não |
| `GET` | `/api/v1/health` | Verifica a saúde da API e a conectividade com o banco de dados. | Não |
| `GET` | `/api/v1/livros` | Lista todos os livros de forma paginada. Aceita query params `?page` e `?per_page`. | Não |
| `GET` | `/api/v1/livros/<id>` | Busca um livro específico pelo seu `id` numérico. | Não |
| `GET` | `/api/v1/livros/filter/price` | Filtra os livros por uma faixa de preço. Aceita query params `?min` e `?max`. | Não |
| `GET` | `/api/v1/categories` | Retorna uma lista com todas as categorias de livros únicas. | Não |
| `GET` | `/api/v1/livros/stats` | Retorna estatísticas (contagem e preço médio) agrupadas por categoria. | Não |
| `GET` | `/api/v1/livros/stats/overview` | Retorna um resumo com estatísticas gerais de todos os livros. | Não |
| `POST` | `/api/v1/trigger-scrape` | Inicia o processo de web scraping em segundo plano (operação assíncrona). | Sim (JWT) |
---
