from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # avoid clash with default User
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username

class Locker(models.Model):
    STATUS = (
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('deactivated', 'Deactivated')
    )
    locker_number = models.CharField(max_length=10, unique=True)
    location = models.CharField(max_length=100, default='Main Area')
    status = models.CharField(max_length=20, choices=STATUS, default='available')
    is_occupied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.locker_number

class Reservation(models.Model):
    locker = models.ForeignKey(Locker, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('locker', 'released_at')

    def __str__(self):
        return f"{self.user.username} - {self.locker.locker_number}"