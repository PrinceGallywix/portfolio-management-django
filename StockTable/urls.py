

"""StockTable URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from stockInformation.views import CustomLoginView
from django.contrib.auth.views import LogoutView
from stockInformation.views import update_stock_table, clientView, adminView


urlpatterns = [
    url(r'^portfolio/', update_stock_table, name='update_stock_table'),
    url(r'client/', clientView, name='client_view'),
    url(r'^admin/', admin.site.urls),
    url(r'^adminview/', adminView, name = 'adminView'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page = 'login'), name='logout'),
]
