
from . import views
from django.urls import path
from rest_framework.authtoken import views as authviews

urlpatterns = [
    path(
        "get-token",
        views.generate_new_token,
        name="get-new-token",
    ),
    path('api/user_auth/', authviews.obtain_auth_token),

]