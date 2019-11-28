"""cpm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from cpmindex import views as index_views

urlpatterns = [
    # path('', include('dashboard.urls')),

    path('', include('cpmindex.urls')),
    # path('', index_views.CpmIndexView.as_view(), name='index'),
    path('auth/', include('cpmauth.urls')),
    path('basic/', include('basic.urls')),
    path('select/', include('cpmselect.urls')),
    path('purchase/', include('cpmpurchase.urls')),
    path('photo/', include('cpmphoto.urls')),
    path('mobile/', include('mobile.urls')),
    path('sale/', include('sale.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


