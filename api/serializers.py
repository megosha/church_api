from django.utils import timezone

from api import models
from rest_framework import serializers

from api.tasks import ViewTasks


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Profile
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(read_only=True, source='section.title')

    class Meta:
        model = models.News
        fields = '__all__'


class TaskParams(serializers.Serializer):
    chat_id = serializers.IntegerField()
    text = serializers.CharField()
    delete_after = serializers.DurationField(required=False)


class TaskSerializer(serializers.Serializer):
    task = serializers.CharField()
    clocked_time = serializers.DateTimeField(default=None)
    delta_time = serializers.DurationField(required=False, min_value=10)
    params = TaskParams()

    def validate_task(self, value):
        if not hasattr(ViewTasks, value):
            raise serializers.ValidationError('Task not found')
        return value

    def validate(self, data):
        data = super().validate(data)
        if 'delta_time' in data:
            if data['clocked_time']:
                raise serializers.ValidationError('Only one clocked_time or delta_time allowed')
            data['clocked_time'] = timezone.now() + data['delta_time']
            del data['delta_time']
        return data
