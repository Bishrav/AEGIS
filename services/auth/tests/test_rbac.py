import unittest

from aegis_auth.rbac import Permission, Role, UserContext, authorize


class RbacTest(unittest.TestCase):
    def test_viewer_has_read_access_only(self):
        user = UserContext("viewer-1", Role.VIEWER)
        self.assertTrue(authorize(user, Permission.VIEW_INCIDENTS))
        self.assertTrue(authorize(user, Permission.VIEW_EVIDENCE))
        self.assertFalse(authorize(user, Permission.EDIT_INCIDENTS))

    def test_admin_has_all_permissions(self):
        user = UserContext("admin-1", Role.ADMIN)
        self.assertTrue(all(authorize(user, permission) for permission in Permission))


if __name__ == "__main__":
    unittest.main()
