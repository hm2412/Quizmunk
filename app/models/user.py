from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    # creates and saves regular user in db
    def create_user(self, email_address, password=None, **extra_fields):
        if not email_address:
            raise ValueError('The Email Address field must be set')
        email_address = self.normalize_email(email_address)
        user = self.model(email_address=email_address, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # creates and saves a superuser(admin) in the db
    def create_superuser(self, email_address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email_address, password, **extra_fields)

    # retrieves user by email address
    # this function seems unnecessary?
    def get_by_natural_key(self, email_address):
        return self.get(email_address=email_address)


class User(AbstractBaseUser, PermissionsMixin):
    STUDENT = 'student'
    TUTOR = 'tutor'

    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TUTOR, 'Tutor'),
    ]

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email_address = models.EmailField(unique=True)
    role = models.CharField(
        max_length=7,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # Required (unique identifier)
    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_address

    class Meta:
        ordering = ['email_address']