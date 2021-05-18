from django import forms


class AddStockForm(forms.Form):
    add_stock = forms.CharField(label='add_stock', max_length=10)
    stocks_bought = forms.IntegerField(label='stocks_bought')
    buying_price = forms.DecimalField(label='buying_price', min_value=0)
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
    sector = forms.ChoiceField(choices=sector_list)


class DateForm(forms.Form):
    da = forms.DateField(label = 'date')

class RemoveStockForm(forms.Form):
    remove_stock = forms.CharField(label='remove_stock')

