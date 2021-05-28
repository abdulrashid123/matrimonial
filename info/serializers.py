from rest_framework import serializers
from .models import Profile,ProfileImage
import datetime


class ProfileSerializers(serializers.ModelSerializer):


    class Meta:
        model = Profile
        fields = '__all__'


class ImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = '__all__'
