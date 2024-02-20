from functools import wraps
from flask import request, current_app, jsonify
import logging
import hashlib
import hmac


def verify_signature(payload, signature):
    is_expecting_signature = hmac.new(
        bytes(current_app.config["app_secret"], "latin-1"),  # Added closing parenthesis
        message=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(is_expecting_signature, signature)


def signature_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Hub-Signature-256", "")[7:]
        if not verify_signature(request.data.decode("utf-8"), signature):
            logging.info("signature verification failed")
            return jsonify({"status": "error", "message": "invalid signature"}), 403
        return f(*args, **kwargs)
    return decorated_function
