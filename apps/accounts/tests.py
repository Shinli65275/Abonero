from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.businesses.models import Branch, Business

from .models import EmployeeProfile, Role, User
from .permissions import IsAdmin, IsAdminOrSupervisor, IsCollector


class UserModelTests(TestCase):
    def setUp(self):
        self.business = Business.objects.create(name="Muebles Demo")

    def test_username_is_normalized_to_lowercase(self):
        user = User.objects.create_user("  Juan.Perez ", "pass12345", business=self.business)
        self.assertEqual(user.username, "juan.perez")

    def test_username_unique_ignoring_case(self):
        User.objects.create_user("maria", "pass12345", business=self.business)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("MARIA", "pass12345", business=self.business)

    def test_default_role_is_collector(self):
        user = User.objects.create_user("cobrador1", "pass12345", business=self.business)
        self.assertEqual(user.role, Role.COLLECTOR)
        self.assertTrue(user.is_collector_role)

    def test_user_has_uuid_pk(self):
        user = User.objects.create_user("u1", "pass12345", business=self.business)
        self.assertEqual(len(str(user.pk)), 36)

    def test_profile_created_automatically(self):
        user = User.objects.create_user("u2", "pass12345", business=self.business)
        self.assertTrue(EmployeeProfile.objects.filter(user=user).exists())

    def test_regular_user_requires_business(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("sinempresa", "pass12345")

    def test_superuser_is_admin_and_may_lack_business(self):
        su = User.objects.create_superuser("root", "pass12345")
        self.assertEqual(su.role, Role.ADMIN)
        self.assertTrue(su.is_staff and su.is_superuser)

    def test_invalid_role_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("x", "pass12345", business=self.business, role="HACKER")

    def test_password_is_hashed(self):
        user = User.objects.create_user("u3", "pass12345", business=self.business)
        self.assertNotEqual(user.password, "pass12345")
        self.assertTrue(user.check_password("pass12345"))


class RolePermissionTests(TestCase):
    def setUp(self):
        business = Business.objects.create(name="Demo")
        self.admin = User.objects.create_user("a", "pass12345", business=business, role=Role.ADMIN)
        self.sup = User.objects.create_user("s", "pass12345", business=business, role=Role.SUPERVISOR)
        self.col = User.objects.create_user("c", "pass12345", business=business, role=Role.COLLECTOR)
        self.inactive = User.objects.create_user(
            "i", "pass12345", business=business, role=Role.ADMIN, is_active=False
        )
        self.factory = APIRequestFactory()

    def _check(self, perm_class, user):
        request = self.factory.get("/")
        request.user = user
        return perm_class().has_permission(request, None)

    def test_is_admin(self):
        self.assertTrue(self._check(IsAdmin, self.admin))
        self.assertFalse(self._check(IsAdmin, self.sup))
        self.assertFalse(self._check(IsAdmin, self.col))

    def test_is_admin_or_supervisor(self):
        self.assertTrue(self._check(IsAdminOrSupervisor, self.admin))
        self.assertTrue(self._check(IsAdminOrSupervisor, self.sup))
        self.assertFalse(self._check(IsAdminOrSupervisor, self.col))

    def test_is_collector(self):
        self.assertTrue(self._check(IsCollector, self.col))
        self.assertFalse(self._check(IsCollector, self.admin))

    def test_inactive_user_denied(self):
        self.assertFalse(self._check(IsAdmin, self.inactive))

    def test_anonymous_denied(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(self._check(IsAdmin, AnonymousUser()))


class InitBusinessCommandTests(TestCase):
    def test_creates_business_and_branch_once(self):
        call_command("init_business", "--name", "Mi Empresa", verbosity=0)
        call_command("init_business", "--name", "Otra", verbosity=0)
        self.assertEqual(Business.objects.count(), 1)
        self.assertEqual(Branch.objects.filter(business__name="Mi Empresa", name="Matriz").count(), 1)
