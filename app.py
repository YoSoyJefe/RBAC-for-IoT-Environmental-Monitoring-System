from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

CONFIG = {
    "bad_pm25_threshold": 35.0
}

ROLES = ["Admin", "Technician", "Analyst", "Viewer"]

API_KEYS = {
    "admin-key": "Admin",
    "tech-key": "Technician",
    "analyst-key": "Analyst",
    "viewer-key": "Viewer"
}

PERMISSIONS = {
    "Admin": {"read_raw", "read_summary", "update_config"},
    "Technician": {"read_raw", "read_summary"},
    "Analyst": {"read_summary"},
    "Viewer": {"read_basic"}
}

ACCESS_LOG = []


def log_access(role, endpoint, allowed):
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "role": role,
        "endpoint": endpoint,
        "allowed": allowed
    }
    ACCESS_LOG.append(entry)


def get_role_from_request():
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None
    return API_KEYS.get(api_key)


def require_permission(permission):
    def checker():
        role = get_role_from_request()
        if role is None:
            log_access("Unknown", request.path, False)
            return jsonify({"error": "Missing or invalid API key"}), 401

        allowed_perms = PERMISSIONS.get(role, set())
        if permission not in allowed_perms:
            log_access(role, request.path, False)
            return jsonify({"error": "Forbidden for role: {}".format(role)}), 403

        log_access(role, request.path, True)
        return None
    return checker


def generate_sensor_data():
    data = {
        "pm25": round(random.uniform(5.0, 80.0), 2),
        "pm10": round(random.uniform(10.0, 100.0), 2),
        "co2": round(random.uniform(350.0, 1500.0), 1),
        "temperature": round(random.uniform(18.0, 32.0), 1),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return data


def summarize_air_quality(pm25_value):
    threshold = CONFIG.get("bad_pm25_threshold", 35.0)
    if pm25_value <= threshold:
        return "Air quality is acceptable."
    else:
        return "Air quality is poor. PM2.5 above threshold."


@app.route("/raw", methods=["GET"])
def get_raw_data():
    check = require_permission("read_raw")()
    if check is not None:
        return check

    sensor_data = generate_sensor_data()
    return jsonify({"type": "raw", "data": sensor_data})


@app.route("/summary", methods=["GET"])
def get_summary():
    role = get_role_from_request()
    if role is None:
        log_access("Unknown", request.path, False)
        return jsonify({"error": "Missing or invalid API key"}), 401

    if "read_summary" in PERMISSIONS.get(role, set()) or "read_basic" in PERMISSIONS.get(role, set()):
        log_access(role, request.path, True)
        sensor_data = generate_sensor_data()
        message = summarize_air_quality(sensor_data["pm25"])
        return jsonify({
            "type": "summary",
            "pm25": sensor_data["pm25"],
            "message": message,
            "timestamp": sensor_data["timestamp"]
        })
    else:
        log_access(role, request.path, False)
        return jsonify({"error": "Forbidden for role: {}".format(role)}), 403


@app.route("/config", methods=["POST"])
def update_config():
    check = require_permission("update_config")()
    if check is not None:
        return check

    body = request.get_json(silent=True) or {}
    if "bad_pm25_threshold" in body:
        try:
            new_value = float(body["bad_pm25_threshold"])
            CONFIG["bad_pm25_threshold"] = new_value
            return jsonify({"status": "updated", "bad_pm25_threshold": new_value})
        except ValueError:
            return jsonify({"error": "Invalid threshold value"}), 400

    return jsonify({"error": "No configuration fields provided"}), 400


@app.route("/logs", methods=["GET"])
def get_logs():
    role = get_role_from_request()
    if role != "Admin":
        log_access(role if role else "Unknown", request.path, False)
        return jsonify({"error": "Forbidden"}), 403

    log_access(role, request.path, True)
    return jsonify({"logs": ACCESS_LOG})


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "time": time.strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == "__main__":
    app.run(debug=True)
