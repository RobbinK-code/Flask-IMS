import unittest

from app import create_app


class InventoryApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_get_inventory_returns_empty_list_initially(self):
        response = self.client.get("/inventory")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create_inventory_item(self):
        payload = {"name": "Laptop", "sku": "LAP-001", "quantity": 10, "price": 999.99}

        response = self.client.post("/inventory", json=payload)

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data["name"], "Laptop")
        self.assertEqual(data["sku"], "LAP-001")
        self.assertEqual(data["quantity"], 10)
        self.assertEqual(data["price"], 999.99)
        self.assertIn("id", data)

    def test_update_inventory_item(self):
        self.client.post(
            "/inventory",
            json={"name": "Mouse", "sku": "MOU-001", "quantity": 5, "price": 25.0},
        )

        response = self.client.patch(
            "/inventory/1",
            json={"quantity": 8, "price": 27.5},
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["quantity"], 8)
        self.assertEqual(data["price"], 27.5)

    def test_delete_inventory_item(self):
        self.client.post(
            "/inventory",
            json={"name": "Keyboard", "sku": "KEY-001", "quantity": 3, "price": 49.99},
        )

        response = self.client.delete("/inventory/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"message": "Item deleted"})

    def test_fetch_product_details_from_external_api(self):
        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        def fake_fetch(url, timeout=5):
            return FakeResponse({"product": {"product_name": "Sample Product", "brands": "TestBrand"}})

        from app import fetch_product_details

        with unittest.mock.patch("app.urlopen", side_effect=fake_fetch):
            data = fetch_product_details("123456789")

        self.assertEqual(data["product_name"], "Sample Product")
        self.assertEqual(data["brands"], "TestBrand")


if __name__ == "__main__":
    unittest.main()
