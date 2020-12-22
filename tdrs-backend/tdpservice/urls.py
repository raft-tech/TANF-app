"""Define Django routing."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic.base import RedirectView
from .users.api.authorization_check import AuthorizationCheck
from .users.api.login import TokenAuthorizationOIDC
from .users.api.login_redirect_oidc import LoginRedirectOIDC
from .users.api.logout import LogoutUser
from .users.api.logout_redirect_oidc import LogoutRedirectOIDC

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login", TokenAuthorizationOIDC.as_view(), name="login"),
    path("login/oidc", LoginRedirectOIDC.as_view(), name="oidc-auth"),
    path("logout", LogoutUser.as_view(), name="logout"),
    path("logout/oidc", LogoutRedirectOIDC.as_view(), name="oidc-logout"),
    path("auth_check", AuthorizationCheck.as_view(), name="authorization-check"),
    path("users/", include("tdpservice.users.urls")),
    path("stts/", include("tdpservice.stts.urls")),
    path("reports/", include("tdpservice.reports.urls")),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add 'prefix' to all urlpatterns to make it easier to version/group endpoints
urlpatterns = [path("v1/", include(urlpatterns))]
