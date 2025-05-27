from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Subscription, Recipe


User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(
                follower=request.user,
                author=obj
            ).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )
        read_only_fields = fields

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit', 10**10)
        recipes = obj.recipes.all()
        recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = fields
