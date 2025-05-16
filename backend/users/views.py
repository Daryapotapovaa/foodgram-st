from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserAvatarSerializer, UserWithRecipesSerializer
from rest_framework import serializers
from api.pagination import CustomPagination
from django.shortcuts import get_object_or_404
from .models import Subscription


User = get_user_model()

class CustomUserViewSet(DjoserUserViewSet):
    pagination_class = CustomPagination
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
            
        elif request.method == 'DELETE':
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
        pagination_class=CustomPagination
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            following__follower=user
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
        following = get_object_or_404(User, id=id)

        if request.method == 'POST':

            if user == following:
                return Response(
                    {'error': 'Невозможно подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription, created = Subscription.objects.get_or_create(
                follower=user,
                following=following
            )
            if not created:
                return Response(
                    {'error': 'Невозможно подписаться дважды'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(
                subscription.following,
                context={'request': request}
            )
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        elif request.method == 'DELETE':

            subscription = Subscription.objects.filter(
                follower=user,
                following=following
            )
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)