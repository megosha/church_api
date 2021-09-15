import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import override_settings, TestCase
from django.urls import reverse
from django_celery_beat.models import PeriodicTask
from rest_framework.authtoken.models import Token

from api.views import TaskView


class TaskViewTestCase(TestCase):
    view_cls = TaskView

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @override_settings(CELERY_TASK_EAGER_PROPAGATES=True)
    def test_post_task(self):
        path = reverse('api:task')
        response = self.client.post(path)
        self.assertEqual(response.status_code, 401)

        user = User.objects.create()
        self.assertTrue(Token.objects.exists())

        task = 'post2group'
        headers = dict(HTTP_AUTHORIZATION=f"Token {user.auth_token.key}")
        params = dict(chat_id=123, text='test', delete_after='10')
        data = dict(task=task, params=params)

        return_value = {'ok': True, 'result': {
            'message_id': 773,
            'from': {'id': 33, 'is_bot': True, 'first_name': 'bot', 'username': 'bot_bot'},
            'chat': {'id': 40, 'first_name': 'user', 'username': 'testuser', 'type': 'private'},
            'date': 1631589602, 'text': 'test'}}
        with patch('front.methods.TGram.send_message') as mock:
            mock.return_value = return_value
            response = self.client.post(path, json.dumps(data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        del_task = PeriodicTask.objects.get(name=f'ViewTasks {task} - api.tasks.delete_message')
        self.assertEqual(del_task.kwargs, '{"chat_id": 123, "message_id": 773}')

        data['delta_time'] = '10'
        response = self.client.post(path, json.dumps(data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        post_task = PeriodicTask.objects.get(name=f'ViewTasks {task}')
        self.assertEqual(post_task.kwargs, '{"chat_id": 123, "text": "test", "delete_after": "10"}')

