from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import user_passes_test
from tdpservice.users.models import User
from rest_framework.authtoken.models import Token


def can_get_new_token(user):
    return user.is_authenticated and user.is_ofa_sys_admin

def token_is_valid(token):
    token = Token.objects.get(key=token)
    # TODO: add token expiration check
    return token is not None

@user_passes_test(can_get_new_token, login_url='/login/')
@api_view(['GET'])
def generate_new_token(request):
    """
    Generates new token for the API user.
    """
    if request.method == 'GET':
        user = User.objects.get(username=request.user)
        token = Token.objects.get_or_create(user=user)
        return Response(str(token))
