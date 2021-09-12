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


class TaskSerializer(serializers.Serializer):
    task = serializers.CharField()
    clocked_time = serializers.DateTimeField(default=None)
    delta_time = serializers.DurationField(default=None, min_value=10)
    params = serializers.DictField(required=False)

    def validate_task(self, value):
        if not hasattr(ViewTasks, value):
            raise serializers.ValidationError('Task not found')
        return value

    def validate(self, data):
        data = super().validate(data)
        if data['delta_time']:
            if data['clocked_time']:
                raise serializers.ValidationError('Only one clocked_time or delta_time allowed')
            data['clocked_time'] = timezone.now() + data['delta_time']
        return data
