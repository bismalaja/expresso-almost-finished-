from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.mainPage, name="mainPage"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("mainpage/", views.mainPage, name="mainPage"),
    path("tickets/", views.tickets, name="tickets"),
    path("membership/", views.membership, name="membership"),
    path("create_ticket/", views.create_ticket, name="create_ticket"),
    path("buy_ticket/<int:ticket_id>/", views.buy_ticket, name="buy_ticket"),
    path("ticket_confirmation/<int:ticket_id>/", views.confirm_ticket, name="ticket_confirmation"),
    path("view_tickets/<int:route_id>/", views.view_tickets, name="view_tickets"),    
    path("buy_daily_ticket/<int:ticket_id>/", views.buy_daily_ticket, name="buy_daily_ticket"),
    path("buy_weekly_ticket/<int:ticket_id>/", views.buy_weekly_ticket, name="buy_weekly_ticket"),
    path("buy_monthly_ticket/<int:ticket_id>/", views.buy_monthly_ticket, name="buy_monthly_ticket"),
    path("active_memberships/", views.active_memberships, name="active_memberships"),
    
    
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="myApp/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="mainPage"), name="logout"),
]