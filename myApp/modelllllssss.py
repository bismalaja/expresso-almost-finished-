from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    TYPE_CHOICES = [
        ('one-way', 'One-Way'),
        ('24-hour', '24-Hour'),
        ('week', 'Week'),
        ('month', 'Month'),
    ]
    
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    ticket_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    available_seats = models.IntegerField()

    def __str__(self):
        return f"{self.ticket_type} from {self.departure} to {self.arrival}"

class UserTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=20)
    confirmed = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=10)
    payment_info = models.CharField(max_length=100)
    credit_used = models.FloatField(default=0)
    
    def __str__(self):
        return f"Ticket for {self.user.username} ({self.ticket_type})"

    def generate_qr_code(self):
        # Logic to generate QR code with ticket info
        pass
