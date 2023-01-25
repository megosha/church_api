from django.test import SimpleTestCase

from front import methods


class YoutubeGetIdTestCase(SimpleTestCase):

    def test_youtube_get_id(self):
        cases = {
            'https://www.youtube.com/live/_9Y-WO3vQz4': '_9Y-WO3vQz4',
            'https://youtu.be/5xbfXgYq4ac': '5xbfXgYq4ac',
            'https://www.youtube.com/live/5xbfXgYq4ac?feature=share': '5xbfXgYq4ac'
        }
        for path, result in cases.items():
            self.assertEqual(methods.youtube_get_id(path), result)
