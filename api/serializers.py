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
    delayed = serializers.BooleanField(default=False)
    clocked_time = serializers.DateTimeField(required=False)
    params = serializers.DictField(required=False)

    def validate_task(self, value):
        if not hasattr(ViewTasks, value):
            raise serializers.ValidationError('Task not found')
        return value

    def validate(self, data):
        data = super().validate(data)
        if data['delayed'] and not data['clocked_time']:
            raise serializers.ValidationError('Delayed task must have clocked_time')
        return data
