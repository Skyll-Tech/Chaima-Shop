from django import forms

from Account.models import Shopper

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Shopper
        fields = ["first_name", "last_name", "email", "password"]