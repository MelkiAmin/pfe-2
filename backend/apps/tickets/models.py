import uuid
from django.db import models
from django.conf import settings


class TicketType(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default=0)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ticket_types'

    def __str__(self):
        return f'{self.event.title} - {self.name}'

    @property
    def available_quantity(self):
        return self.quantity - self.quantity_sold

    @property
    def is_available(self):
        return self.available_quantity > 0


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        USED = 'used', 'Used'
        REFUNDED = 'refunded', 'Refunded'

    ticket_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, related_name='tickets')
    event = models.ForeignKey('events.Event', on_delete=models.PROTECT, related_name='tickets')
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    qr_code = models.ImageField(upload_to='tickets/qr/', null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ticket #{self.ticket_number} - {self.event.title}'