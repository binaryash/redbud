from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Three roles: Manager, Trainer, and Employee
    """

    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('trainer', 'Trainer'),
        ('employee', 'Employee'),
    )

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = [
            ('can_create_training', 'Can create training'),
            ('can_add_training_modules', 'Can add training modules'),
            ('can_view_all_trainings', 'Can view all trainings'),
            ('can_manage_employees', 'Can manage employees'),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_manager(self):
        return self.role == 'manager'

    def is_trainer(self):
        return self.role == 'trainer'

    def is_employee(self):
        return self.role == 'employee'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.assign_role_permissions()

    def assign_role_permissions(self):
        """Automatically assign permissions based on user role"""
        from django.contrib.auth.models import Group

        self.groups.clear()

        if self.role == 'manager':
            group, created = Group.objects.get_or_create(name='Manager')
        elif self.role == 'trainer':
            group, created = Group.objects.get_or_create(name='Trainer')
        else:
            group, created = Group.objects.get_or_create(name='Employee')

        self.groups.add(group)


class Training(models.Model):
    """
    Training model to store training information
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.IntegerField(help_text="Number of days for the training")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trainings')
    assigned_trainer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_trainings',
        limit_choices_to={'role': 'trainer'}
    )
    employees = models.ManyToManyField(
        User,
        related_name='trainings',
        limit_choices_to={'role': 'employee'},
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Training'
        verbose_name_plural = 'Trainings'

    def __str__(self):
        return self.name


class TrainingModule(models.Model):
    """
    Training Module model to store individual modules within a training
    """
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Order of the module in the training")
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_modules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['training', 'order']
        verbose_name = 'Training Module'
        verbose_name_plural = 'Training Modules'
        unique_together = ['training', 'order']

    def __str__(self):
        return f"{self.training.name} - {self.title}"
