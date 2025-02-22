import os
from app import app  # Ensure your app instance is properly created in app/__init__.py
import logging
from flask import Flask, jsonify

# Assuming 'app' is your Flask instance:
@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled exception: %s", e)
    # Optionally, return a JSON response with error details (for debugging only!)
    return jsonify(error=str(e)), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)  # No debug=True in production