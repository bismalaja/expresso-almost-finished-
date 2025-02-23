from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from .models import TrainRoute, Ticket, UserTicket, User, ActiveMembership
from .forms import TicketForm, UserRegistrationForm, UserUpdateForm
from io import BytesIO

def index(request):
    return render(request, "myApp/mainPage.html", {})

def mainPage(request):
    return render(request, "myApp/mainPage.html", {})

def login_view(request):
    if request.method == 'POST':
        print("POST request received")  # Debug statement
        form = AuthenticationForm(request.POST)  # Pass request.POST as data
        if form.is_valid():
            print("Form is valid")  # Debug statement
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            print(f"Attempting to authenticate user: {email}")  # Debug statement
            user = authenticate(request, username=email, password=password)
            if user is not None:
                print(f"User authenticated: {user.email}")  # Debug statement
                login(request, user)
                messages.success(request, 'Login successful')
                return redirect('mainPage')
            else:
                messages.error(request, 'Invalid email or password.')
                return redirect('/login/')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('/login/')
    if request.method == 'GET':
        return render(request, 'myApp/login.html', {'form': AuthenticationForm()})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserRegistrationForm()
    return render(request, 'myApp/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('mainPage')

def dashboard(request):
    routes = TrainRoute.objects.all()
    active_memberships = []
    if request.user.is_authenticated:
        active_memberships = ActiveMembership.objects.filter(user=request.user, end_date__gt=timezone.now())
    return render(request, "myApp/dashboard.html", {"routes": routes, "active_memberships": active_memberships})

def trains(request):
    routes = TrainRoute.objects.all()
    return render(request, "myApp/trains.html", {"routes": routes})

def tickets(request):
    tickets = Ticket.objects.all()
    user_tickets, active_memberships = [], []
    if request.user.is_authenticated:
        user_tickets = UserTicket.objects.filter(user=request.user)
        active_memberships = ActiveMembership.objects.filter(user=request.user)
    return render(request, "myApp/active_memberships.html", {"tickets": tickets, "user_tickets": user_tickets, "active_memberships": active_memberships})

def membership(request):
    active_memberships = ActiveMembership.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, "myApp/membership.html", {"active_memberships": active_memberships})


@login_required
def profile(request):
    form = UserUpdateForm(request.POST, instance=request.user) if request.method == 'POST' else UserUpdateForm(instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your profile has been updated!')
        return redirect('profile')
    user_tickets = UserTicket.objects.filter(user=request.user)
    return render(request, 'myApp/profile.html', {'form': form, 'user_tickets': user_tickets})

def create_active_membership(user_ticket):
    active_membership = ActiveMembership(user=user_ticket.user, user_ticket=user_ticket)
    active_membership.save()
    return active_membership

@login_required
def create_ticket(request):
    if request.user.is_staff:
        if request.method == "POST":
            pass
        return render(request, "myApp/create_ticket.html")
    return redirect('login')

def process_ticket_purchase(request, ticket_id, template_name):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Debug statement
            user_ticket = form.save(commit=False)
            user_ticket.user = request.user
            user_ticket.ticket = ticket
            user_ticket.confirmed = True
            user_ticket.save()
            active_membership = create_active_membership(user_ticket)
            # send_mail(
            #     "Your Ticket Purchase Confirmation",
            #     f"You have purchased a {ticket.ticket_type} ticket. Valid until {active_membership.end_date}.",
            #     'from@example.com',
            #     [request.user.email],
            #     fail_silently=False,
            # )
            messages.success(request, f'Your {ticket.get_ticket_type_display()} ticket was purchased successfully!')
            return redirect('active_memberships')
        else:
            print("Form is not valid")  # Debug statement
            print
    else:
        form = TicketForm()
    return render(request, template_name, {'form': form, 'ticket': ticket})

@login_required(login_url='login')
def buy_ticket(request, ticket_id):
    return process_ticket_purchase(request, ticket_id, "myApp/buy_ticket.html")

@login_required(login_url='login')
def confirm_ticket(request, ticket_id):
    user_ticket = get_object_or_404(UserTicket, id=ticket_id)
    try:
        active_membership = user_ticket.active_membership
    except ActiveMembership.DoesNotExist:
        active_membership = create_active_membership(user_ticket)
    return render(request, "myApp/confirm_ticket.html", {'ticket': user_ticket, 'active_membership': active_membership})

def view_tickets(request, route_id):
    route = get_object_or_404(TrainRoute, id=route_id)
    available_tickets = Ticket.objects.filter(route=route)
    return render(request, "myApp/view_tickets.html", {'route': route, 'tickets': available_tickets})

@login_required(login_url='login')
def buy_daily_ticket(request, ticket_id):
    return process_ticket_purchase(request, ticket_id, "myApp/buy_daily_ticket.html")

@login_required(login_url='login')
def buy_weekly_ticket(request, ticket_id):
    return process_ticket_purchase(request, ticket_id, "myApp/buy_weekly_ticket.html")

@login_required(login_url='login')
def buy_monthly_ticket(request, ticket_id):
    return process_ticket_purchase(request, ticket_id, "myApp/buy_monthly_ticket.html")

@login_required(login_url='login')
def active_memberships(request):
    active_memberships = ActiveMembership.objects.filter(user=request.user, end_date__gt=timezone.now()).order_by('end_date')
    expired_memberships = ActiveMembership.objects.filter(user=request.user, end_date__lte=timezone.now()).order_by('-end_date')
    return render(request, "myApp/active_memberships.html", {'active_memberships': active_memberships, 'expired_memberships': expired_memberships})
