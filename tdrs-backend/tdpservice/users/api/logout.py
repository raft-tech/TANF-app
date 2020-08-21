"""Login.gov/logout is redirected to this endpoint end a django user session."""

import os
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import logout


# logout user
class LogoutUser(APIView):
    """Define method to log out user from Django."""

    def get(self, request, *args, **kwargs):
        """Destroy user session."""
        try:
            logout(request)
        except Exception:
            return HttpResponse({
                "system: User logged out of Login.gov/ Django sessions terminated before local logout"}, status=status.HTTP_200_OK)
        response = HttpResponseRedirect(os.environ['FRONTEND_BASE_URL'])
        response.delete_cookie('id_token')
        return response
