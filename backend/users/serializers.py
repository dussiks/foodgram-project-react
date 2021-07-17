from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueTogetherValidator

from .models import CustomUser, Follow


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password')



class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all(),
    )

    class Meta:
        model = Follow
        fields = ('follower', 'following')
        validators = [UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=['follower', 'following']
        )]

    def validate(self, data):
        request = self.context['request']
        if request.user == data.get('following'):
            raise serializers.ValidationError(
                'User can not subscribe on himself.'
            )
        return data
