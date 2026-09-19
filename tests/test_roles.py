"""Role hierarchy replaces the seven-table ASP.NET Identity role machinery."""

from models.user import Role, role_satisfies


def test_superadmin_satisfies_admin_requirement():
    assert role_satisfies(Role.SUPERADMIN, Role.ADMIN)


def test_admin_does_not_satisfy_superadmin_requirement():
    assert not role_satisfies(Role.ADMIN, Role.SUPERADMIN)


def test_each_role_satisfies_itself():
    assert role_satisfies(Role.ADMIN, Role.ADMIN)
    assert role_satisfies(Role.SUPERADMIN, Role.SUPERADMIN)
