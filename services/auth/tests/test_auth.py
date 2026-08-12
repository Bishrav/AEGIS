import unittest

from aegis_auth.app import decode_token, issue_token
from aegis_auth.rbac import Role, UserContext


class AuthTest(unittest.TestCase):
    def test_token_round_trip_preserves_identity_and_role(self):
        user = UserContext("user-analyst", Role.ANALYST)
        token = issue_token(user, "a" * 32)
        self.assertEqual(decode_token(token, "a" * 32), user)

    def test_wrong_secret_is_rejected(self):
        token = issue_token(UserContext("user-viewer", Role.VIEWER), "a" * 32)
        with self.assertRaises(Exception):
            decode_token(token, "b" * 32)


if __name__ == "__main__":
    unittest.main()
