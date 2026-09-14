"""Rota de páginas — serve a interface web do chat."""

from flask import Blueprint, render_template

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Renderiza a interface de chat."""
    return render_template("index.html")
