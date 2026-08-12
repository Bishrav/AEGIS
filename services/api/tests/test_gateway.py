import unittest

from aegis_api.app import health, require
from aegis_auth.rbac import Permission, Role, UserContext


class GatewayTest(unittest.TestCase):
    def test_gateway_health_identifies_application_surface(self):
        self.assertEqual(health(), {"status": "ok", "service": "api-gateway"})

    def test_rbac_boundary_keeps_viewer_out_of_mutation_permissions(self):
        from aegis_auth.rbac import authorize

        viewer = UserContext("viewer", Role.VIEWER)
        self.assertTrue(authorize(viewer, Permission.VIEW_INCIDENTS))
        self.assertFalse(authorize(viewer, Permission.EDIT_INCIDENTS))


if __name__ == "__main__":
    unittest.main()
