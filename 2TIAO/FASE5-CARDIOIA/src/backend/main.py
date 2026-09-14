"""
CardioIA — Assistente Cardiológico Conversacional
====================================================
Ponto de entrada da aplicação Flask.
"""

import logging

from flask import Flask

from api.routes.chat import chat_bp
from api.routes.pages import pages_bp
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

# templates/ e static/ vivem em src/frontend (pasta irmã de src/backend) — não há um
# servidor de frontend separado aqui (diferente do projeto Dasa/Genera): é o próprio
# Flask que renderiza o HTML e serve os assets, então só apontamos os caminhos.
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
app.secret_key = settings.FLASK_SECRET_KEY

app.register_blueprint(pages_bp)
app.register_blueprint(chat_bp)


if __name__ == "__main__":
    app.run(debug=True)
