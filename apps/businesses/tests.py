from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Branch, Business


class BusinessModelTests(TestCase):
    def test_business_has_uuid_pk_and_defaults(self):
        b = Business.objects.create(name="Demo")
        self.assertEqual(len(str(b.pk)), 36)
        self.assertEqual(b.currency, "MXN")
        self.assertTrue(b.is_active)

    def test_branch_name_unique_per_business(self):
        b = Business.objects.create(name="Demo")
        Branch.objects.create(business=b, name="Centro")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Branch.objects.create(business=b, name="Centro")

    def test_same_branch_name_allowed_in_other_business(self):
        b1 = Business.objects.create(name="A")
        b2 = Business.objects.create(name="B")
        Branch.objects.create(business=b1, name="Centro")
        Branch.objects.create(business=b2, name="Centro")
        self.assertEqual(Branch.objects.count(), 2)
