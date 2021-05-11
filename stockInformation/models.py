from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# class Stocks(models.Model):
#     symbol = models.CharField(max_length=200)
#     name = models.CharField(max_length=200)
#     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     change = models.DecimalField(max_digits=10, decimal_places=2)
#     stocks_owned = models.IntegerField()
#     buying_price = models.DecimalField(max_digits=10, decimal_places=2)
#     balance = models.DecimalField(max_digits=10, decimal_places=2)

    # def __str__(self):
    #     return self.symbol, self.name, self.price, self.change


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.OneToOneField(User, related_name='client', on_delete= models.CASCADE)
    invest_horizon = models.IntegerField("Wanted invest horizon, in months")

    def __str__(self):
        return self.client.get_username()

class Managerr(models.Model):
    id = models.AutoField(primary_key=True)
    managerr = models.OneToOneField(User, related_name='managerr', on_delete= models.CASCADE)

    def __str__(self):
        return self.managerr.get_username()


class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    risk_wanted_types = models.TextChoices("Wanted risk", 'EXTRA BIG IF_NEEDED FEW ZERO')
    risk_wanted = models.CharField(blank= True, choices= risk_wanted_types.choices, max_length= 20)
    current_risk = models.IntegerField("Current risk rate of a portfolio, from 1 to 100")
    cash_inserted = models.FloatField("How much an investor brought to company")
    current_cash = models.IntegerField("How much money do portfolio contains")
    owner = models.ForeignKey(Client, verbose_name="Who own this portfolio", on_delete= models.CASCADE)
    employee = models.ForeignKey(Managerr, verbose_name="Who run this portfolio", on_delete= models.CASCADE)

    def __str__(self):
        return str(self.owner.client.get_username())

class Sector(models.Model):
    id = models.AutoField(primary_key=True)
    sector_list = (('Energy','Energy'),
                   ('Materials','Materials'),
                   ('Industrials','Industrials'),
                   ('Consumer Discretionary','Consumer Discretionary'),
                   ('Consumer Staples','Consumer Staples'),
                   ('Health Care','Health Care'),
                   ('Financials','Financials'),
                   ('Information Technology','Information Technology'),
                   ('Telecommunication Services','Telecommunication Services'),
                   ('Utilities','Utilities'),
                   ('Real Estate','Real Estate'))
    sector = models.TextField(choices=sector_list)

    def __str__(self):
        return self.sector


class Stocks(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.CharField("Ticker on stock exchange", max_length= 8)
    name = models.CharField(max_length= 50)
    buying_price = models.FloatField()
    price = models.FloatField()

    date_of_buying = models.DateField()
    dividend_yield = models.FloatField()
    beta_coef = models.FloatField()
    sector = models.ForeignKey(Sector, on_delete= models.CASCADE)
    risk_coef = models.FloatField()
    stocks_owned = models.IntegerField()

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.symbol, self.name, self.buying_price, self.price, self.portfolio)