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

app = Flask(__name__)
app.secret_key = settings.FLASK_SECRET_KEY

app.register_blueprint(pages_bp)
app.register_blueprint(chat_bp)


if __name__ == "__main__":
    app.run(debug=True)
