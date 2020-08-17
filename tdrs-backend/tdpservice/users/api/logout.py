"""Log out the user from Django."""

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import logout


# logout user
class LogoutUser(APIView):
    """Define method to log out user from Django."""

    def get(self, request, *args, **kwargs):
        """Destroy user session."""
        logout(request)
        return Response({
            "system": "User logged out"
        }, status=status.HTTP_200_OK)
