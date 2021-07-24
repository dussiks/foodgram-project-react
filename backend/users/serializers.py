from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import CustomUser
from recipes_api.models import Follow


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = UserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, author):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return (current_user == author) or Follow.objects.filter(
            user=current_user, author=author
        ).exists()


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=150,
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
