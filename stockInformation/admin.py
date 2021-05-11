from django.contrib import admin
from django.contrib.auth.models import User
from .models import Client, Stocks, Portfolio, Sector, Managerr

admin.site.register(Client)
admin.site.register(Stocks)
admin.site.register(Portfolio)
admin.site.register(Sector)
admin.site.register(Managerr)



# Register your models here.
