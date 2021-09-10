from django.conf import settings
from django.test import override_settings, TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from api.views import TaskView


class TaskViewTestCase(TestCase):

    view_cls = TaskView

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_settings(CELERY_TASK_EAGER_PROPAGATES=True)
    def test_post_task(self):
        response = self.client.post(reverse('api:task'))
        self.assertEqual(response.status_code, 401)

        user = User.objects.create()
        self.assertTrue(Token.objects.exists())

        headers = dict(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
        response = self.client.post(reverse('api:task'), **headers)
        self.assertEqual(response.status_code, 200)
