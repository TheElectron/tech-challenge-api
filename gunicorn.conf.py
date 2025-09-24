import os
# O endereço IP e a porta onde o Gunicorn irá escutar.
bind = "0.0.0.0:8000"
# Número de workers (processos) para lidar com requisições.
workers = (os.cpu_count() * 2) + 1

# Nível de log. 
# Opções: 'debug', 'info', 'warning', 'error', 'critical'
loglevel = "info"
accesslog = "-"
errorlog = "-"
timeout = 120
