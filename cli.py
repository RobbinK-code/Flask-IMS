import argparse
import json
import urllib.request

BASE_URL = "http://127.0.0.1:5000"


def request_json(method: str, path: str, payload: dict | None = None) -> object:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--sku", required=True)
    add_parser.add_argument("--quantity", type=int, required=True)
    add_parser.add_argument("--price", type=float, required=True)

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("item_id", type=int)
    update_parser.add_argument("--quantity", type=int)
    update_parser.add_argument("--price", type=float)

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("item_id", type=int)

    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("query")

    args = parser.parse_args()

    if args.command == "list":
        print(json.dumps(request_json("GET", "/inventory"), indent=2))
    elif args.command == "add":
        payload = {
            "name": args.name,
            "sku": args.sku,
            "quantity": args.quantity,
            "price": args.price,
        }
        print(json.dumps(request_json("POST", "/inventory", payload), indent=2))
    elif args.command == "update":
        payload = {}
        if args.quantity is not None:
            payload["quantity"] = args.quantity
        if args.price is not None:
            payload["price"] = args.price
        print(json.dumps(request_json("PATCH", f"/inventory/{args.item_id}", payload), indent=2))
    elif args.command == "delete":
        print(json.dumps(request_json("DELETE", f"/inventory/{args.item_id}"), indent=2))
    elif args.command == "fetch":
        print(json.dumps(request_json("GET", f"/products/{args.query}"), indent=2))


if __name__ == "__main__":
    main()
