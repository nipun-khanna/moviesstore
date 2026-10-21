from django import forms

class TopBuyersForm(forms.Form):
    size = forms.IntegerField(label='How many users', min_value=1, max_value=1000, required =False)

