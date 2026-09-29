import os
import sys
import logging
from flask import Flask, request, jsonify, send_from_directory

# Đảm bảo import AutomationBridge được từ thư mục src
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from automation_bridge import AutomationBridge

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ChatServer")

# Cấu hình đường dẫn web tĩnh
WEB_DIR = os.path.join(os.path.dirname(current_dir), "web")

app = Flask(__name__, static_folder=WEB_DIR)

# Khởi tạo Automation Bridge
bridge = AutomationBridge()

@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/katex/<path:filename>")
def serve_katex(filename):
    return send_from_directory(os.path.join(WEB_DIR, "katex"), filename)

@app.route("/ontology.html")
def ontology_page():
    return send_from_directory(WEB_DIR, "ontology.html")

@app.route("/vis-network.min.js")
def vis_network_js():
    return send_from_directory(WEB_DIR, "vis-network.min.js")





@app.route("/corekb.html")
def corekb_page():
    return send_from_directory(WEB_DIR, "corekb.html")

@app.route("/api/corekb")
def corekb():
    """Tra ve toan bo mang luoi Core KB (facts + fact_edges) de ve visualization."""
    import sqlite3
    kb_path = os.path.join(os.path.dirname(current_dir), "core_kb.db")
    try:
        conn = sqlite3.connect(kb_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, type, name, label, description FROM facts")
        nodes = [{"id": r["id"], "label": r["label"] or r["name"], "type": r["type"], "name": r["name"]} for r in cur.fetchall()]
        cur.execute("SELECT source_id, target_id, relation, weight FROM fact_edges")
        edges = [{"from": r["source_id"], "to": r["target_id"], "relation": r["relation"]} for r in cur.fetchall()]
        conn.close()
        return jsonify({"nodes": nodes, "edges": edges})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ontology")
def ontology():
    """Tra ve toan bo do thi tri thuc (nodes + edges) de ve visualization."""
    import sqlite3
    ont_path = os.path.join(os.path.dirname(current_dir), "ontology.db")
    try:
        conn = sqlite3.connect(ont_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, name, tier, category FROM nodes")
        nodes = [{"id": r["id"], "label": r["name"], "tier": r["tier"], "category": r["category"]} for r in cur.fetchall()]
        cur.execute("SELECT source_id, target_id, relation, weight FROM edges")
        edges = [{"from": r["source_id"], "to": r["target_id"], "relation": r["relation"]} for r in cur.fetchall()]
        conn.close()
        return jsonify({"nodes": nodes, "edges": edges})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Thiếu tham số 'message'"}), 400
        
    user_message = data["message"]
    logger.info(f"Received message from user: {user_message}")
    
    try:
        # Chạy ReAct Loop (Quá trình này có thể mất 40-60s)
        answer = bridge.run_react_loop(user_message)
        return jsonify({"answer": answer})
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = 7860
    logger.info(f"Starting Chat Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
