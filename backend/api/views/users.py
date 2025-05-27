from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from api.serializers.users import UserAvatarSerializer, UserWithRecipesSerializer
from api.pagination import LimitPageNumberPagination
from django.shortcuts import get_object_or_404
from recipes.models import Subscription


User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitPageNumberPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        methods=["PUT", "DELETE"],
        detail=False,
        url_path='me/avatar',
        permission_classes=[permissions.IsAuthenticated]
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            avatar = request.data.get('avatar')

            if avatar:
                serializer = UserAvatarSerializer(
                    user,
                    data=request.data,
                    partial=True,
                    context={'request': request}
                )

                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(
                    {'avatar': user.avatar.url},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        if user.avatar:
            user.avatar.delete()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserWithRecipesSerializer,
        pagination_class=LimitPageNumberPagination
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            authors__follower=user
        ).prefetch_related("recipes")
        pages = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method != 'POST':
            get_object_or_404(
                Subscription, follower=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if user == author:
            raise ValidationError('Невозможно подписаться на себя')

        subscription, created = Subscription.objects.get_or_create(
            follower=user,
            author=author
        )
        if not created:
            raise ValidationError(
                f'Невозможно подписаться на {author.username} дважды'
            )

        serializer = self.get_serializer(
            subscription.author,
            context={'request': request}
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )
