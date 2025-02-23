from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, UserTicket, Ticket

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=255)
    last_name = forms.CharField(required=True, max_length=255)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]  # Set username to email
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class AuthenticationForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            print(f"Attempting to authenticate user: {email}")  # Debug statement
            user = authenticate(username=email, password=password)
            if user is None:
                print("Authentication failed: Invalid credentials")  # Debug statement
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                print("Authentication failed: Account is inactive")  # Debug statement
                raise forms.ValidationError("This account is inactive.")
        else:
            print("Authentication failed: Missing email or password")  # Debug statement
            raise forms.ValidationError("Please provide both email and password.")

        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class TicketForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit/Debit Card'),
        ('paypal', 'Credit')
    ]
    
    payment_type = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect
    )
    
    card_number = forms.CharField(
        required=False,
        max_length=19,
        widget=forms.TextInput(attrs={
            'placeholder': '1234 5678 9012 3456',
            'autocomplete': 'cc-number'
        })
    )
    
    expiry_date = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={
            'placeholder': 'MM/YY',
            'autocomplete': 'cc-exp'
        })
    )
    
    cvv = forms.CharField(
        required=False,
        max_length=4,
        widget=forms.TextInput(attrs={
            'placeholder': '123',
            'autocomplete': 'cc-csc'
        })
    )
    
    card_holder = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'John Doe',
            'autocomplete': 'cc-name'
        })
    )
    
    credit_used = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        initial=0
    )

    class Meta:
        model = UserTicket
        fields = ['payment_type', 'credit_used']  # Only include fields that map directly to model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the ticket field initialization since we're not using it in the form

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')

        if payment_type == 'credit_card':
            required_fields = ['card_number', 'expiry_date', 'cvv', 'card_holder']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'{field.replace("_", " ").title()} is required')
            
            if cleaned_data.get('card_number'):
                cleaned_data['payment_info'] = f"Card ending in {cleaned_data['card_number'][-4:]}"

        return cleaned_data
