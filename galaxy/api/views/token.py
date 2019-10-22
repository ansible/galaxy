import logging
import requests

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication

from galaxy.api.views import base_views
from galaxy.api.serializers import TokenSerializer
from galaxy.common.github import get_github_api_url

__all__ = [
    'TokenView',
    'UserTokenView',
]

logger = logging.getLogger(__name__)
User = get_user_model()


class UserTokenView(base_views.RetrieveUpdateAPIView):
    model = Token
    serializer_class = TokenSerializer
    authentication_classes = (SessionAuthentication,)

    def get_object(self):
        user_id = self.kwargs[self.lookup_field]
        try:
            user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            raise PermissionDenied()
        instance, created = Token.objects.get_or_create(user=user)
        self.check_object_permissions(self.request, instance)
        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        instance.delete()
        instance = Token.objects.create(user=user)
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class TokenView(base_views.APIView):
    """
    Allows ansible-galaxy CLI to retrieve an auth token. This will be
    deprecated with the deprecation of `ansible-galaxy`.
    """

    def post(self, request, *args, **kwargs):
        """
        Uses a GitHub token to authenticate the user, and returns
        a Galaxy Token on success.
        """
        gh_user = None
        user = None
        token = None
        github_token = request.data.get('github_token', None)

        if github_token is None:
            raise ValidationError({'detail': "Invalid request."})

        try:
            git_status = requests.get(get_github_api_url())
            git_status.raise_for_status()
        except requests.exceptions.RequestException as err:
            if err.response.status_code == 101:

            raise ValidationError({
                'detail': "Error accessing GitHub API. Please try again later."
            })
        except Exception:
            raise ValidationError({
                'detail': "Error accessing GitHub API. Please try again later."
            })

        try:
            header = dict(Authorization='token ' + github_token)
            gh_user = requests.get(
                get_github_api_url() + '/user', headers=header
            )
            gh_user.raise_for_status()
            gh_user = gh_user.json()
            if hasattr(gh_user, 'message'):
                raise ValidationError({'detail': gh_user['message']})
        except Exception:
            raise ValidationError({
                'detail': "Error accessing GitHub with provided token."
            })

        if SocialAccount.objects.filter(
                provider='github', uid=gh_user['id']).count() > 0:
            user = SocialAccount.objects.get(
                provider='github', uid=gh_user['id']).user
        else:
            msg = (
                "Galaxy user not found. You must first log into Galaxy using "
                "your GitHub account."
            )
            raise ValidationError({'detail': msg})

        if Token.objects.filter(user=user).count() > 0:
            token = Token.objects.filter(user=user)[0]
        else:
            token = Token.objects.create(user=user)
            token.save()
        result = dict(token=token.key, username=user.username)
        return Response(result, status=status.HTTP_200_OK)
