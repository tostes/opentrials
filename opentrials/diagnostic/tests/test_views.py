import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DumpDataViewTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.staff_user = user_model.objects.create_user(
            username="staff",
            password="password",
            is_staff=True,
        )
        self.client.force_login(self.staff_user)

    def test_dumpdata_page_renders_template(self):
        response = self.client.get(reverse("diagnostic:dumpdata"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "diagnostic/dumpdata.html")

    def test_dumpdata_returns_json_for_specific_app(self):
        response = self.client.get(reverse("diagnostic:dumpdata_app", args=["auth"]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = json.loads(response.content)
        self.assertTrue(any(item["model"] == "auth.user" for item in payload))

    def test_dumpdata_post_allows_multiple_apps(self):
        response = self.client.post(reverse("diagnostic:dumpdata"), {"apps": ["auth"]})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("choices_fixture.json", response["Content-Disposition"])
