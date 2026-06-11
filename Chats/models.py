from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    name_user = models.CharField(max_length=50)
    lastName_user = models.CharField(max_length=50)
    photo_user = models.ImageField(blank=True, null=True, upload_to='imagenes/')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name_user', 'lastName_user']

    def __str__(self):
        return self.name_user


class chat(models.Model):
    name_chat= models.CharField(max_length=50)
    time_chat= models.DateTimeField(default=timezone.now)
    block_chat= models.BooleanField()
    chat_grupal = models.BooleanField(default=False, null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='chats_admin')

    def __str__(self):
        return self.name_chat


class participant(models.Model):
    user= models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    chat= models.ForeignKey(chat, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.name_user #f"{self.user.name_user}-{self.chat.name_chat}"


class message(models.Model):
    text_message= models.TextField(blank=True, null=True)
    time_message= models.DateTimeField(default=timezone.now)
    view_message= models.BooleanField(default=False)
    file_message= models.FileField(blank=True, null=True)
    image_message= models.ImageField(blank=True, null=True)
    resend_message= models.BooleanField(default=False)

    chat= models.ForeignKey(chat, on_delete=models.SET_NULL, blank=True, null=True)
    user= models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.text_message #f"{self.user.name_user}-{self.chat.name_chat}"


class favorite(models.Model):
    user= models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    chat= models.ForeignKey(chat, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.name_user #f"{self.user.name_user}-{self.chat.name_chat}"


class contact(models.Model):

    user_owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="contacts_owner")
    user_contact = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="contacts_added")

    def __str__(self):
        return f"{self.user_owner.name_user}-{self.user_contact.name_user}"






    
