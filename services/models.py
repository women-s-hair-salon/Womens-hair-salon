from django.db import models
from accounts.models import CustomUser


class Categories(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    image = models.ImageField(upload_to='categories_images/',null=True, blank=True)
    text=models.TextField()
    slug = models.SlugField()
    def __str__(self):
        return self.name
# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    duration=models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=3)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services_images/',null=True, blank=True)
    text=models.TextField()
    slug = models.SlugField()

    def __str__(self):
        return self.name
class Reservation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Customer who books
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()  # Booking date
    time = models.TimeField()  # Booking time
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user} - {self.service} on {self.date} at {self.time}"


