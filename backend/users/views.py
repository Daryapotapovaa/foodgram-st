from djoser.views import UserViewSet as DjoserUserViewSet
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserAvatarSerializer
from rest_framework import serializers
from api.pagination import CustomPagination
from django.shortcuts import get_object_or_404


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