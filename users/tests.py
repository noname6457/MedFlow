import json

from django.test import Client, TestCase


class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = Client(
            enforce_csrf_checks=True
        )

        self.client.get("/api/auth/me/")

    def post_json(self, url, data):
        csrf_token = self.client.cookies["csrftoken"].value

        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

    def test_registration_and_login(self):
        register_response = self.post_json(
            "/api/auth/register/",
            {
                "username": "testpatient",
                "email": "test@example.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "password": "MedFlowTest!2026",
            }
        )

        self.assertEqual(
            register_response.status_code,
            201
        )

        login_response = self.post_json(
            "/api/auth/login/",
            {
                "username": "testpatient",
                "password": "MedFlowTest!2026",
            }
        )

        self.assertEqual(
            login_response.status_code,
            200
        )

        me_response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            me_response.status_code,
            200
        )

        self.assertEqual(
            me_response.json()["username"],
            "testpatient"
        )

        logout_response = self.post_json(
            "/api/auth/logout/",
            {}
        )

        self.assertEqual(
            logout_response.status_code,
            200
        )

        me_response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            me_response.status_code,
            401
        )