import unittest
from rbac import RBAC, Role, User

class TestRBAC(unittest.TestCase):
    def test_role_creation(self):
        role = Role("admin", "Administrator Role")
        self.assertEqual(role.name, "admin")
        self.assertEqual(role.description, "Administrator Role")

    def test_user_creation(self):
        ruser = Role("user")
        reditor = Role("editor")
        user = User("john_doe", [ruser, reditor])
        self.assertEqual(user.name, "john_doe")
        self.assertSetEqual(user.roles, set([reditor, ruser]))

    def test_add_role_to_user(self):
        ruser = Role("user")
        reditor = Role("editor")
        user = User("jane_doe", [ruser])
        user.add_role(reditor)
        self.assertSetEqual(user.roles, set([reditor, ruser]))

    def test_remove_role_from_user(self):
        user = User("joe_smith", [Role("editor")])
        user.remove_role("editor")
        self.assertSetEqual(user.roles, set())

    def test_resource_add_rule(self):
        rbac = RBAC()
        Role("admin")
        rbac.resource_add_rule('admin', "GET", "/api/resource")
        self.assertTrue(rbac.is_rule_allowed("admin", "GET", "/api/resource"))

    def test_validate_access(self):
        rbac = RBAC()
        User("john_doe", [Role("test")])
        rbac.resource_add_rule('test', "api", "/api/resource")
        self.assertTrue(rbac.validate(username='john_doe', method='api', resource='/api/resource'))
