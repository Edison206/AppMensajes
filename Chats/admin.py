from django.contrib import admin
from .models import User, chat, participant, message, favorite, contact

admin.site.register(User)
admin.site.register(chat)
admin.site.register(participant)
admin.site.register(message)
admin.site.register(favorite)
admin.site.register(contact)

# Register your models here.
