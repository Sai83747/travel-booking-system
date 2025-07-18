from django.db import models
from django.db.models import TimeField
from django.core.exceptions import ValidationError

# ============================================
# ✅ UserProfile Model (Base User Data)
# ============================================
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('travel_agent', 'Travel Agent'),
        ('user', 'User'),
    )

   
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.email} ({self.role})'


# ============================================
# ✅ Destination Model
# ============================================
class Destination(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ============================================
# ✅ Booking Model
# ============================================


# ============================================
class Admin(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'admin'},
        related_name='admin_profile'
    )
    
    def __str__(self):
        return f'Admin: {self.user_profile.display_name or self.user_profile.email}'
class Hotel(models.Model):
    name = models.CharField(max_length=255)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    available_rooms = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Hotel {self.name} in {self.destination.name}'
# ============================================
# ✅ Travel Agent Model
# ============================================
class TravelAgent(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'travel_agent'},
        related_name='travel_agent_profile'
    )
    
    def __str__(self):
        return f'Travel Agent: {self.user_profile.display_name or self.user_profile.email}'
# ============================================
# ✅ Payment Model
# ============================================
class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    source = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='departing_flights')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='arriving_flights')
    available_seats = models.PositiveIntegerField()
    flight_icon_url = models.URLField(blank=True, null=True)
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination cannot be the same.")
    
    def __str__(self):
        return f'Flight {self.flight_number} ({self.source.name} → {self.destination.name})'

class Package(models.Model):
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='package_sources')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='package_destinations')
    is_available = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image_url = models.URLField(blank=True, null=True)
    duration_days = models.PositiveIntegerField()

    # ✅ Optional Many-to-Many Relationships
    hotels = models.ManyToManyField('Hotel', blank=True, related_name='package_hotels')
    flights = models.ManyToManyField('Flight', blank=True, related_name='package_flights')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination cannot be the same.")

    def __str__(self):
        return f'Package {self.name} ({self.source.name} → {self.destination.name})'

class DestinationConnection(models.Model):
    source = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='source_connections')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='destination_connections')
    distance = models.IntegerField()

# ============================================
# ✅ Booking Model
# ============================================
class Booking(models.Model): 
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    CATEGORY_CHOICES = (
        ('flight', 'Flight'),
        ('package', 'Package'),
        ('hotel', 'Hotel'),
    )

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='bookings')
    source = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='source_bookings', blank=True, null=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_people = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    Date = models.TimeField(auto_now_add=True, blank=True, null=True)

    # ✅ Only one hotel and one package per booking
    flights = models.ManyToManyField(Flight, blank=True, related_name='bookings')
    hotels = models.ForeignKey(Hotel, on_delete=models.SET_NULL, blank=True, null=True, related_name='hotel_bookings')
    packages = models.ForeignKey(Package, on_delete=models.SET_NULL, blank=True, null=True, related_name='package_bookings')

    def __str__(self):
        return f'Booking by {self.user.display_name} for {self.destination.name} ({self.category})'

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f'Payment for Booking {self.booking.id} - {self.status}'


# ============================================
# ✅ Review Model
# ============================================
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Generic relation to Hotel, Flight, or Package
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Review {self.rating} by {self.user.display_name} on {self.content_type} ID {self.object_id}"
