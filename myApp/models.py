from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

class TrainRoute(models.Model):
    train_line = models.CharField(max_length=255)
    distance = models.IntegerField(help_text="Distance in km")
    # Remove price from TrainRoute since it will be in Ticket
    image = models.ImageField(blank=True, null=True)
    snazzy_map = models.URLField(blank=True, null=True)

    def get_stops_list(self):
        return [station.name for station in self.stations.all()]

    def __str__(self):
        return self.train_line


class Station(models.Model):
    name = models.CharField(max_length=255)
    route = models.ForeignKey(TrainRoute, on_delete=models.CASCADE, related_name='stations')
    
    def __str__(self):
        return self.name
    
class Ticket(models.Model):
    TYPE_CHOICES = [
        ('day', '24 hours'),
        ('week', 'Week'),
        ('month', 'Month'),
    ]
    
    route = models.ForeignKey(TrainRoute, on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in euros")  # Added price field

    def __str__(self):
        return f"{self.ticket_type} for {self.route.train_line} (€{self.price})"

class UserTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=130)
    payment_info = models.CharField(max_length=100)
    credit_used = models.FloatField(default=0)
    
    def __str__(self):
        return f"Ticket for {self.user.email} ({self.ticket.ticket_type})"

    def generate_qr_code(self):
        # QR code logic
        pass

class ActiveMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_memberships')
    user_ticket = models.OneToOneField(UserTicket, on_delete=models.CASCADE, related_name='active_membership')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        # Set end_date based on ticket type if not explicitly provided
        if not self.end_date:
            if self.user_ticket.ticket.ticket_type == 'day':
                self.end_date = self.start_date + timedelta(days=1)
            elif self.user_ticket.ticket.ticket_type == 'week':
                self.end_date = self.start_date + timedelta(weeks=1)
            elif self.user_ticket.ticket.ticket_type == 'month':
                # Approximate a month as 30 days
                self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return timezone.now() <= self.end_date
    
    @property
    def days_remaining(self):
        if not self.is_active:
            return 0
        remaining = self.end_date - timezone.now()
        return max(0, remaining.days)
    
    def __str__(self):
        status = "Active" if self.is_active else "Expired"
        return f"{status} membership for {self.user.email} - {self.user_ticket.ticket}"