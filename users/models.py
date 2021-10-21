from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin, User
from django.contrib.postgres.fields import JSONField
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.mixins import CreatedAndUpdatedMixin, UUIDMixin
from users.constants import PHONE_REGEX,USER_TYPE


class PosUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if extra_fields.get('user_type') == 'U':
            user = self.model(
                **extra_fields
            )
            user.set_password(password)
            user.save(using=self._db)
            return user

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self._create_user(
            email,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class PosUser(AbstractBaseUser, PermissionsMixin, CreatedAndUpdatedMixin, UUIDMixin):
    email = models.EmailField(
        verbose_name='email address', max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('designates whether user can log into the adminm site.')
    )
    mobile = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                PHONE_REGEX,
                message='Invalid mobile number',
                code='invalid_phone'
            )
        ],
        null=True
    )
    user_type = models.CharField(
        max_length=1,
        choices=USER_TYPE,
        default='C'
    )
    extra_data = JSONField(null=True, blank=True)
    objects = PosUserManager()

    USERNAME_FIELD = 'email'

    def get_fullname(self):
        if self.first_name or self.last_name:
            return ((self.first_name or '') + ' ' + (self.last_name or ''))
        return ''

    class Meta:
        unique_together = ('mobile', 'user_type', )

    def __str__(self):
        return "{}".format(self.email or self.mobile)
