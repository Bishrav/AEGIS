import unittest

from aegis_api.app import login


class GatewayLoginTest(unittest.TestCase):
    def test_gateway_login_returns_identity(self):
        from fastapi import Response

        result = login({"username": "analyst", "password": "analyst-dev"}, Response())
        self.assertEqual(result, {"user_id": "user-analyst", "role": "ANALYST"})


if __name__ == "__main__":
    unittest.main()
