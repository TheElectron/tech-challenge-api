<<<<<<< HEAD
# tech-challenge-api
=======
# Tech Challenge Api

## Executando o web scraping
> python3 scripts/scraper.py

## Executando a API
> python3 api/app.py

## Gerando a chave privada
> python3 -c "import secrets; print(secrets.token_hex(32))"

## Swagger
http://127.0.0.1:5000/apidocs/

## Gunicorn
gunicorn --config gunicorn.conf.py "api.app:create_app()"


TBD

* Descrição do projeto e arquitetura.
* Instruções de instalação e configuração.
* Documentação das rotas da API.
* Exemplos de chamadas com requests/responses.
* Instruções para execução.
>>>>>>> feature/web-scraping
