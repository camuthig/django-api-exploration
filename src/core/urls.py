"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path

from cbv_api.views import router as cbv_router
from functional.drf_views import router as drf_router
from functional.views import router as functional_router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("functional/", functional_router.urls("functional")),
    path("drf/", drf_router.urls("drf")),
    path("cbv/", cbv_router.urls("cbv"))
]
