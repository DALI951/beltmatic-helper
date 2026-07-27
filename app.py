from flask import Flask, render_template, jsonify, request
import os
import sys
import socket

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solver import solve, format_solution, get_needed_buildings
from upgrades import (load_upgrades, load_progress, save_progress,
                      get_all_upgrade_status, get_level_requirements, get_hub_status)

app = Flask(__name__)

HOST = "127.0.0.1"
PORT = 5000


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def api_solve():
    data = request.json
    target = data.get("target", 0)
    extractable = data.get("extractable", [1])
    operations = data.get("operations", ["+"])

    if target <= 0:
        return jsonify({"found": False, "error": "Target must be positive"}), 400

    path, error = solve(target, extractable, operations, max_steps=20)

    if path:
        steps = format_solution(path)
        buildings = get_needed_buildings(path)
        return jsonify({
            "found": True,
            "steps": steps,
            "buildings": buildings,
            "length": len(path) - 1
        })
    else:
        return jsonify({"found": False, "error": error or "No solution found. Try adding more operations or numbers."})


@app.route("/api/upgrades")
def api_upgrades():
    return jsonify(get_all_upgrade_status())


@app.route("/api/progress", methods=["GET"])
def api_get_progress():
    return jsonify(load_progress())


@app.route("/api/progress", methods=["POST"])
def api_save_progress():
    data = request.json
    save_progress(data)
    return jsonify({"ok": True})


@app.route("/api/hub")
def api_hub():
    return jsonify(get_hub_status())


@app.route("/api/levels")
def api_levels():
    return jsonify(get_level_requirements())


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, port)) == 0


def open_browser():
    import webbrowser
    import time
    for _ in range(20):
        if is_port_in_use(PORT):
            break
        time.sleep(0.2)
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    import threading

    if is_port_in_use(PORT):
        print(f"\n  Port {PORT} already in use.")
        print(f"  If Beltmatic Helper is already running, use http://{HOST}:{PORT}\n")
        import webbrowser
        webbrowser.open(f"http://{HOST}:{PORT}")
    else:
        timer = threading.Timer(0.5, open_browser)
        timer.daemon = True
        timer.start()
        print(f"\n  ========================================")
        print(f"    Beltmatic Helper is running!")
        print(f"    Open: http://{HOST}:{PORT}")
        print(f"    Keep this window open while playing.")
        print(f"  ========================================\n")
        app.run(debug=False, host=HOST, port=PORT)
