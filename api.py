"""
api-auto-quote — Moteur de cotation automatique d'assurance auto
Déployé sur /opt/api-auto-quote/ (VPS Ubuntu 24.04 LTS)

Routes :
  POST /receive  → reçoit le JSON canonique et le stocke en mémoire
  GET  /show     → retourne le dernier JSON reçu
  GET  /health   → retourne le statut et la date du dernier JSON reçu
"""

from flask import Flask, request, jsonify
from datetime import datetime, timezone
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Stockage en mémoire du dernier JSON reçu
state = {
    "last_payload": None,
    "received_at": None,
}


# ---------------------------------------------------------------------------
# POST /receive
# ---------------------------------------------------------------------------

@app.route("/receive", methods=["POST"])
def receive():
    """
    Reçoit le JSON canonique envoyé par le formulaire frontend.

    Structure attendue :
    {
        "token":      "<UUID>",
        "vehicle":    { ... },
        "subscriber": { ... },
        "drivers":    [ ... ],
        "history":    { ... }
    }
    """
    payload = request.get_json(silent=True)

    if payload is None:
        logger.warning("Requête reçue sans corps JSON valide")
        return jsonify({"status": "error", "message": "Corps JSON invalide ou absent"}), 400

    token = payload.get("token", "<sans token>")
    logger.info("Payload reçu — token: %s", token)
    logger.info("Contenu complet : %s", payload)

    state["last_payload"] = payload
    state["received_at"] = datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # TODO: mapper les données par assureur
    #   Exemple : mapped = mapper.run(payload)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # TODO: lancer les scrapers par assureur
    #   Exemple : results = scraper_pool.run(mapped)
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # TODO: agréger et retourner les tarifs
    #   Exemple : return jsonify({"status": "ok", "quotes": results})
    # ------------------------------------------------------------------

    return jsonify({
        "status": "received",
        "token": token,
        "received_at": state["received_at"],
        "message": "JSON stocké en mémoire. Mapping et scraping non encore implémentés.",
    }), 200


# ---------------------------------------------------------------------------
# GET /show
# ---------------------------------------------------------------------------

@app.route("/show", methods=["GET"])
def show():
    """Retourne le dernier JSON canonique reçu."""
    if state["last_payload"] is None:
        return jsonify({"status": "empty", "message": "Aucun payload reçu pour l'instant"}), 404

    return jsonify({
        "status": "ok",
        "received_at": state["received_at"],
        "payload": state["last_payload"],
    }), 200


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    """Retourne le statut du service et la date du dernier JSON reçu."""
    return jsonify({
        "status": "ok",
        "service": "api-auto-quote",
        "last_received_at": state["received_at"],
    }), 200


# ---------------------------------------------------------------------------
# Entrée principale
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
