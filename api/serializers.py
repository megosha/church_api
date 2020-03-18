from api import models
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Profile
        fields = '__all__'

    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.url)
