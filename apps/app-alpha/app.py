"""
app-alpha — Flask Web Application #1
Assessment GKE Infrastructure Project
"""

import logging
import os
import time
import random
from flask import Flask, jsonify, Blueprint

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "app": "app-alpha", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

APP_NAME = os.environ.get("APP_NAME", "app-alpha")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENV = os.environ.get("ENV", "development")

# Blueprint for all public/user-facing routes, served under /alpha via Ingress
alpha_bp = Blueprint("alpha", __name__, url_prefix="/alpha")


@alpha_bp.route("/")
def index():
    logger.info("Root endpoint called")
    return jsonify({
        "app": APP_NAME,
        "version": APP_VERSION,
        "env": ENV,
        "status": "healthy",
        "message": "Hello from app-alpha on GKE!"
    })


@alpha_bp.route("/api/data")
def data():
    """Sample data endpoint that simulates latency."""
    start = time.time()
    time.sleep(random.uniform(0.01, 0.1))
    latency_ms = (time.time() - start) * 1000
    logger.info(f"Data endpoint served in {latency_ms:.2f}ms")
    return jsonify({
        "app": APP_NAME,
        "latency_ms": round(latency_ms, 2),
        "data": [{"id": i, "value": random.randint(1, 100)} for i in range(5)]
    })


@alpha_bp.route("/api/error")
def error():
    """Endpoint to simulate errors (for Grafana error-rate panel demo)."""
    if random.random() < 0.3:  # 30% chance of error
        logger.error("Simulated application error triggered")
        return jsonify({"error": "Simulated internal error"}), 500
    return jsonify({"status": "ok"}), 200


# Health/readiness probes stay UN-prefixed — kubelet hits these directly
# on the pod's container port, bypassing the Ingress entirely.
@app.route("/health")
def health():
    """Kubernetes liveness probe endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready")
def ready():
    """Kubernetes readiness probe endpoint."""
    return jsonify({"status": "ready"}), 200


app.register_blueprint(alpha_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} on port {port}")
    app.run(host="0.0.0.0", port=port)