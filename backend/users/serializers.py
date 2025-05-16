from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from .models import Subscription


User = get_user_model()

class CustomUserSerializer(DjoserUserSerializer):
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
             'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url
        else:
            return None

    def get_is_subscribed(self, obj):
        follower = self.context.get('request').user
        if follower.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=follower,
            following=obj
        ).exists()

class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')

        if avatar is None:
            raise serializers.ValidationError(
                'Avatar is required.'
            )
        instance.avatar = avatar
        instance.save()
        return instance
    

class UserWithRecipesSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        from recipes.serializers import ShortRecipeSerializer
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit is not None:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                pass
        return ShortRecipeSerializer(recipes, many=True, context=self.context).data