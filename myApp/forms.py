from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserTicket, Ticket

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class TicketForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('credit', 'Credit'),
        ('card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
    ]
    
    payment_type = forms.ChoiceField(choices=PAYMENT_CHOICES)
    credit_used = forms.FloatField(required=False, initial=0)
    card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Card Number'}))
    expiry_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}))
    cvv = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'CVV', 'autocomplete': 'off'}))
    card_holder = forms.CharField(required=False)
    payment_info = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'autocomplete': 'off'}))

    class Meta:
        model = UserTicket
        fields = ['ticket', 'payment_type', 'credit_used', 'payment_info']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ticket'].queryset = Ticket.objects.all()
        self.fields['ticket'].label_from_instance = lambda obj: f"{obj.ticket_type} for {obj.route.train_line}"

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')

        if payment_type == 'card':
            if not cleaned_data.get('card_number'):
                raise forms.ValidationError("Card number is required for credit card payments")
            if not cleaned_data.get('expiry_date'):
                raise forms.ValidationError("Expiry date is required for credit card payments")
            if not cleaned_data.get('cvv'):
                raise forms.ValidationError("CVV is required for credit card payments")
            
            cleaned_data['payment_info'] = f"Card ending in {cleaned_data.get('card_number')[-4:]}"

        return cleaned_data
