"""malquarium URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from backend.views import *
from malquarium.jwt import MalquariumTokenObtainPairView, MalquariumTokenRefreshView

schema_view = get_schema_view(
    openapi.Info(
        title="Malquarium API",
        default_version='v1',
        description="JSON API for Malquarium",
        contact=openapi.Contact(email="malquarium@drbeni.ch"),
        license=openapi.License(name="GPLv3"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^api(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^api/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('admin/', admin.site.urls),
    path('api/query/<str:search_string>/', SampleList.as_view(), name='sample-list'),
    path('api/samples/', SampleUpload.as_view(), name='sample-upload'),
    path('api/samples/stats/', SampleStats.as_view(), name='sample-stats'),
    re_path('^api/samples/feed/(?P<filter>[^/]+)/(?P<tags>.*)$', SampleFeed.as_view(), name='sample-feed'),
    path('api/samples/<str:sha2>/', SampleDetail.as_view(), name='sample-detail'),
    path('api/samples/download/<str:sample_format>/<str:sha2>/', SampleDownload.as_view(), name='sample-download'),
    path('api/tags/', TagList.as_view(), name='tag-list'),
    path('api/tags/add/<str:tag_name>/<str:sha2>/', add_tag, name='add-tag'),
    path('api/tags/remove/<str:tag_name>/<str:sha2>/', remove_tag, name='remove-tag'),

    path('api/token/reset/', TokenReset.as_view(), name='token-reset'),

    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/auth/token/obtain/', MalquariumTokenObtainPairView.as_view()),
    path('api/auth/token/refresh/', MalquariumTokenRefreshView.as_view()),
    path('api/auth/profile/', ProfileView.as_view(), name='profile-view'),
]
