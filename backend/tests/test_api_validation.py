import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app import app


class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_decode_rejects_oversized_address(self):
        response = self.client.post(
            "/v1/decode",
            json={"address": "a" * 300},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
