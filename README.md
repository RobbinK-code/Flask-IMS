# Flask Inventory Management System

This project provides a small Flask-based inventory management API with CRUD functionality, an external product lookup integration, and a simple CLI for interacting with the service.

## Features

- Create, read, update, and delete inventory items
- Fetch product details from the OpenFoodFacts API by barcode or search term
- Interact with the API through a command-line interface
- Unit tests covering CRUD and product lookup behavior

## Run the API

```bash
python app.py
```

The API will be available at http://127.0.0.1:5000. The root endpoint returns a simple status payload for health checks.

## CLI Examples

```bash
python cli.py list
python cli.py add --name "Laptop" --sku "LAP-001" --quantity 5 --price 899.99
python cli.py update 1 --quantity 8 --price 949.99
python cli.py delete 1
python cli.py fetch 3017620422003
```

## Run Tests

```bash
pytest -q
```
