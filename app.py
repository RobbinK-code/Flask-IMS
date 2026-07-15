from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request, send_from_directory


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(JSON_SORT_KEYS=False)

    if test_config:
        app.config.update(test_config)

    inventory: list[dict[str, Any]] = []
    next_id = 1

    def get_item(item_id: int) -> dict[str, Any] | None:
        for item in inventory:
            if item["id"] == item_id:
                return item
        return None

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({"message": "Flask Inventory Management System API", "status": "ok"})

    @app.route("/inventory", methods=["GET"])
    def list_inventory():
        return jsonify(inventory)

    @app.route("/inventory", methods=["POST"])
    def create_item():
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "JSON object required"}), 400

        required_fields = {"name", "sku", "quantity", "price"}
        missing = required_fields.difference(payload)
        if missing:
            return jsonify({"error": f"Missing fields: {sorted(missing)}"}), 400

        nonlocal next_id
        item = {
            "id": next_id,
            "name": payload["name"],
            "sku": payload["sku"],
            "quantity": payload["quantity"],
            "price": payload["price"],
        }
        inventory.append(item)
        next_id += 1
        return jsonify(item), 201

    @app.route("/inventory/<int:item_id>", methods=["GET"])
    def get_inventory_item(item_id: int):
        item = get_item(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item)

    @app.route("/inventory/<int:item_id>", methods=["PATCH"])
    def update_item(item_id: int):
        item = get_item(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404

        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "JSON object required"}), 400

        for field in ("name", "sku", "quantity", "price"):
            if field in payload:
                item[field] = payload[field]

        return jsonify(item)

    @app.route("/inventory/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id: int):
        item = get_item(item_id)
        if item is None:
            return jsonify({"error": "Item not found"}), 404

        inventory.remove(item)
        return jsonify({"message": "Item deleted"})

    @app.route("/products/<path:query>", methods=["GET"])
    def product_lookup(query: str):
        return jsonify(fetch_product_details(query))

    @app.route("/ui", methods=["GET"])
    def ui():
        return send_from_directory("Frontend", "index.html")

    @app.route('/frontend/<path:filename>', methods=['GET'])
    def frontend_files(filename: str):
        return send_from_directory('Frontend', filename)

    return app


def fetch_product_details(query: str) -> dict[str, Any]:
    query = query.strip()
    if query.isdigit():
        url = f"https://world.openfoodfacts.org/api/v2/product/{query}.json"
    else:
        encoded = quote(query)
        url = (
            "https://world.openfoodfacts.org/cgi/search.pl?"
            f"search_terms={encoded}&search_simple=1&action=process&json=1"
        )

    request = Request(url, headers={"User-Agent": "Flask-IMS/1.0"})
    response = urlopen(request, timeout=5)
    if hasattr(response, "read"):
        payload = json.loads(response.read().decode("utf-8"))
    else:
        payload = response.json()

    if payload.get("product"):
        product = payload["product"]
        return {
            "product_name": product.get("product_name"),
            "brands": product.get("brands"),
        }

    if payload.get("products"):
        product = payload["products"][0]
        return {
            "product_name": product.get("product_name"),
            "brands": product.get("brands"),
        }

    return {}


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
