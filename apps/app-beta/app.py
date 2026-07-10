"""
app-beta — Flask Web Application #2
Assessment GKE Infrastructure Project
"""

import logging
import os
import time
import random
from flask import Flask, jsonify, Blueprint

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "app": "app-beta", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

APP_NAME = os.environ.get("APP_NAME", "app-beta")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
ENV = os.environ.get("ENV", "development")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://app-alpha-svc:8080")

# Blueprint for all public/user-facing routes, served under /beta via Ingress
beta_bp = Blueprint("beta", __name__, url_prefix="/beta")


@beta_bp.route("/")
def index():
    logger.info("Root endpoint called")
    return jsonify({
        "app": APP_NAME,
        "version": APP_VERSION,
        "env": ENV,
        "status": "healthy",
        "message": "Hello from app-beta on GKE!",
        "backend": BACKEND_URL
    })


@beta_bp.route("/api/process")
def process():
    """Simulates a processing endpoint with variable latency."""
    start = time.time()
    # Simulate heavier processing
    time.sleep(random.uniform(0.05, 0.2))
    latency_ms = (time.time() - start) * 1000
    logger.info(f"Process endpoint served in {latency_ms:.2f}ms")
    return jsonify({
        "app": APP_NAME,
        "processed": True,
        "latency_ms": round(latency_ms, 2),
        "items_processed": random.randint(10, 100)
    })


@beta_bp.route("/api/error")
def error():
    """Endpoint to simulate errors (for Grafana error-rate panel demo)."""
    if random.random() < 0.2:  # 20% chance of error
        logger.error("Simulated application error triggered")
        return jsonify({"error": "Simulated processing error"}), 500
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


app.register_blueprint(beta_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} on port {port}")
    app.run(host="0.0.0.0", port=port)