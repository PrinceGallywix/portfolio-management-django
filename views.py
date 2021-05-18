from django.shortcuts import render
from yahoo_finance import Share
import yfinance as yf
import time
import traceback
import decimal
import logging
from .models import Stocks, Sector, Portfolio, Client, Managerr
from .forms import AddStockForm, DateForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
import datetime
import random
from django.template.defaulttags import register
import dateutil
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from django.shortcuts import redirect



# CREATING LOGGER
logger = logging.getLogger('LOG')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class CustomLoginView(LoginView):
    template_name = 'stockInformation/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('update_stock_table')


def logout_view(request):
    logout(request)
    return redirect('login/')

@register.filter(name='lookup')
def lookup(value, arg):
    v ={}
    v = dict(value)
    return v.get(arg)



@login_required(redirect_field_name='login')
def update_stock_table(request):
    print(Portfolio.objects.get())

    try:
        p = Portfolio.objects.get(employee=request.user.managerr)
    except ObjectDoesNotExist:
        return clientView(request)



    stock_list = Stocks.objects.filter(portfolio = p).order_by('price')
    today_date = datetime.date.today().strftime('%Y-%m-%d')

    rw = str(p.risk_wanted)

    if rw == 'EXTRA':
        rwv = 1
    elif rw == 'BIG':
        rwv = 0.8
    elif rw =='IF_NEEDED':
        rwv = 0.6
    elif rw == 'FEW':
        rwv = 0.3
    elif rw == 'ZERO':
        rwv = 0.1



    if 'add_stock' in request.POST:

            form = AddStockForm(request.POST)

            if form.is_valid():  # form validation
                new_stock = request.POST.get("add_stock", "")

                if p.current_cash > float(form.cleaned_data['stocks_bought'])*float(form.cleaned_data['buying_price']):
                    if not Stocks.objects.filter(portfolio = p, symbol=new_stock.upper()):  # stock not already in portfolio

                        logger.info('Adding ' + new_stock.upper() + ' to stock portfolio')
                        print(p.current_cash)

                        try:  # try to add stock to portfolio
                            data = yf.download(new_stock)['Adj Close'].dropna()
                            data = data[-3:-1]
                            d = data[0]
                            d_change = data[1] - data[0]

                            #stock_object = Share(new_stock)
                            new_stock_name = new_stock
                            new_stock_price = d
                            new_stock_change = d_change
                            stocks_owned = form.cleaned_data['stocks_bought']
                            buying_price = form.cleaned_data['buying_price']
                            sec = form.cleaned_data['sector']
                            sector = Sector.objects.get(sector = sec)
                            stock_to_db = Stocks(symbol=new_stock.upper(),
                                                 name=new_stock_name,
                                                 price=new_stock_price,
                                                 buying_price=buying_price,
                                                 date_of_buying = today_date,
                                                 beta_coef = random.uniform(-1, 1),
                                                 sector = sector,
                                                 risk_coef = random.uniform(0, 1),
                                                 dividend_yield = random.uniform(-1, 1),
                                                 stocks_owned=stocks_owned,
                                                 portfolio = p,
                                                 )
                            stock_to_db.save()
                            delta_cash = p.current_cash - float(form.cleaned_data['stocks_bought'])*float(form.cleaned_data['buying_price'])
                            p.current_cash = delta_cash
                            p.save()


                            add_success_message = "Stock successfully added to portfolio!"

                            stock = Stocks.objects.get(symbol=new_stock, portfolio = p)
                            stocks = stock.stocks_owned
                            bprice = stock.buying_price
                            price = stock.price
                            balance = (stocks * price) - (stocks * bprice)
                            #stock.balance = balance
                            stock.save()

                            context = {
                                'stock_list': stock_list,
                                'today_date': today_date,
                                'add_success_message': add_success_message,
                            }
                            return render(request, 'stockInformation/stocks.html', context)

                        except Exception:  # if symbol is not correct
                            traceback.print_exc()
                            pass
                            error_message = "Insert correct symbol!"

                            context = {
                                'stock_list': stock_list,
                                'today_date': today_date,
                                'error_message': error_message,
                            }
                            return render(request, 'stockInformation/stocks.html', context)

                    else:  # if symbol is already in your portfolio
                        stock_exists_message = "Stock is already in your portfolio!"

                        context = {
                            'stock_list': stock_list,
                            'today_date': today_date,
                            'stock_exists_message': stock_exists_message,
                        }
                        return render(request, 'stockInformation/stocks.html', context)

                else:  # if form was incorrectly filled in
                    error_message = "Not enough money!"

                    context = {
                        'stock_list': stock_list,
                        'today_date': today_date,
                        'error_message': error_message,
                    }
                    return render(request, 'stockInformation/stocks.html', context)

            else:  # if form was incorrectly filled in
                error_message = "Invalid form!"

                context = {
                    'stock_list': stock_list,
                    'today_date': today_date,
                    'error_message': error_message,
                }
                return render(request, 'stockInformation/stocks.html', context)

    elif 'remove_stock' in request.POST:  # if user was trying to remove stock from portfolio

        symbol = str(request.POST.get('stock_symbol'))

        if Stocks.objects.filter(portfolio = p, symbol=symbol).count() > 0:  # if inserted stock is in portfolio

            s = Stocks.objects.get(portfolio=p, symbol=symbol)
            logger.info('Removing ' + symbol + ' from stock portfolio')

            p.current_cash = p.current_cash + s.price*s.stocks_owned
            p.save()

            Stocks.objects.filter(portfolio = p,symbol=symbol).delete()
            stock_list = Stocks.objects.filter(portfolio = p).order_by('price')

            delete_success_message = "Stock successfully removed from portfolio!"

            context = {
                'stock_list': stock_list,
                'today_date': today_date,
                'delete_success_message': delete_success_message,

            }
            return render(request, 'stockInformation/stocks.html', context)

    else:  # if there was no POST request - the whole portfolio should be updated
        stocks = Stocks.objects.filter(portfolio = p)  # This returns queryset
        change_dict = {}
        balance_dict = {}

        count_now = p.current_cash
        curr_risk = 0
        for stock in stocks:
            #stock_object = Share(stock.symbol)
            data = yf.download(stock.symbol)['Adj Close'].dropna()
            data = data[-3:-1]
            d = data[-1]
            d_change = data[1] - data[0]

            stock.price = d
            #stock.change = d_change

            balance = (float(stock.stocks_owned) * stock.price) - (float(stock.stocks_owned) * float(stock.buying_price))
            balance_dict[str(stock.symbol)] = balance

            #stock.save(update_fields=['price', 'change', 'balance'])  # do not create new object in db,
            stock.save(update_fields=['price'])
            # update current lines
            change_dict[str(stock.symbol)] = d_change
            count_now += stock.price * stock.stocks_owned

        curr_profit = (count_now-p.cash_inserted)/(p.cash_inserted) * 100
        print(p.cash_inserted,count_now, curr_profit)
        for stock in stock_list:
            curr_risk += ((stock.price * stock.stocks_owned) / count_now) * stock.risk_coef
        delta_risk = rwv - curr_risk

        risk_ok = ''
        if delta_risk > 0.3:
            risk_ok = 'Too low'
        elif delta_risk > -0.2:
            risk_ok = 'OK'
        else:
            risk_ok = 'Too high'

        context = {
            'stock_list': stock_list,
            'today_date': today_date,
            'change_dict': change_dict,
            'portfolio': p,
            'balance_dict': balance_dict,
            'curr_profit': curr_profit,
            'risk_ok': risk_ok,
        }
        logger.info('Refreshing stock list')

        return render(request, 'stockInformation/stocks.html', context)

@login_required(redirect_field_name='login')
def clientView(request):
    try:
        p = Portfolio.objects.get(owner=request.user.client)
    except Exception:
        return logout_view(request)

    stocks = Stocks.objects.filter(portfolio=p)
    count_now = p.current_cash
    print(count_now)
    for stock in stocks:
        data = yf.download(stock.symbol)['Adj Close'].dropna()
        d = data[-1]
        stock.price = d
        stock.save(update_fields=['price'])
        count_now += stock.price * stock.stocks_owned
        print(stock.price, stock.stocks_owned, count_now)

    curr_profit = (count_now - p.cash_inserted) / (p.cash_inserted) * 100
    print(curr_profit)

    context = {
        'portfolio': p,
        'curr_profit': curr_profit,
    }
    return render(request, 'stockInformation/client.html', context)


def adminView(request):
    today_date = datetime.date.today()
    a_month = dateutil.relativedelta.relativedelta(months=1)

    prev_month = today_date - a_month

    if 'start_date' in request.POST:
        prev_month = request.POST.get("start_date")
        prev_month = datetime.datetime.strptime(prev_month, '%Y-%m-%d' )
        prev_month = prev_month.date()
        print(prev_month)

    #prev_month = datetime.datetime.combine(prev_month, datetime.time(0, 0))
    stock_list = Stocks.objects.filter(date_of_buying__gte = prev_month).order_by('date_of_buying')

    ports = Portfolio.objects.filter().order_by('cash_inserted')
    profit_dict = {}
    for p in ports:
        profit_dict[p.owner] = get_profit(p)

    stock_list2 = Stocks.objects.filter(sector__sector='Utilities').order_by('date_of_buying')
    if 'sector' in request.POST:
        sector = request.POST.get("sector")

        stock_list2 = Stocks.objects.filter(sector__sector= sector).order_by('date_of_buying')


    context = {
        'stock_list_1': stock_list,
        'portfolio_list': ports,
        'profit_dict': profit_dict,
        'stock_list_2': stock_list2
    }
    return render(request, 'stockInformation/adminview.html', context)





def get_profit(p):
    stocks = Stocks.objects.filter(portfolio=p)
    count_now = p.current_cash
    curr_risk = 0
    for stock in stocks:
        # stock_object = Share(stock.symbol)
        data = yf.download(stock.symbol)['Adj Close'].dropna()
        data = data[-3:-1]
        d = data[-1]
        stock.price = d
        count_now += stock.price * stock.stocks_owned

    curr_profit = (count_now - p.cash_inserted) / (p.cash_inserted) * 100

    return curr_profit