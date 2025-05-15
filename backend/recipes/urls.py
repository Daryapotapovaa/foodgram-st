from django.urls import path
from .views_redirect import redirect_short_link

urlpatterns = [
    path("s/<int:recipe_id>/", redirect_short_link, name="short-link"),
]