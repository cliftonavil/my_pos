from django.contrib import admin

# Register your models here.
from users.models import PosUser

admin.site.register(PosUser)