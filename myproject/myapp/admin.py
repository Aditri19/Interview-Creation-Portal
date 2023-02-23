from django.contrib import admin

# Register your models here.
from .models import Participant
admin.site.register(Participant) 

from .models import Interview
admin.site.register(Interview)