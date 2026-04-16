from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    from backend.database.models import Base, engine
    Base.metadata.create_all(bind=engine)

    from backend.api.chat import chat_bp
    from backend.api.graphs import graphs_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(graphs_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": "college-roi-advisor"})

    return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5055"))
    create_app().run(host="127.0.0.1", port=port, debug=False)
