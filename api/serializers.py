from api import models
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Profile
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(read_only=True, source='section.title')

    class Meta:
        model = models.News
        fields = '__all__'