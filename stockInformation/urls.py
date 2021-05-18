from django.conf.urls import url
from django.urls import path

from stockInformation.views import CustomLoginView
from .views import *

urlpatterns = [

    #url(r'stocks', update.update_stock_table, name='update_stock_table'),
    url(r'crowdfunding', crowdfunding, name='crowdfunding'),
]
