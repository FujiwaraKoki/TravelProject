from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            user_name=username,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Users(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, default='')
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    create_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    update_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy('TravelApp:home')


class Destinations(models.Model):
    destination_id = models.AutoField(primary_key=True)
    username = models.ForeignKey(Users, on_delete=models.CASCADE, max_length=150, blank=True, null=True)
    destination_name = models.CharField(max_length=150)
    date = models.DateField(verbose_name="旅行した日", blank=False, null=False, default=timezone.now)
    GoogleMapURL = models.URLField()
    TravelRecord = models.CharField(max_length=500)
    picture = models.FileField(upload_to='destination/')
    create_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    update_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'destinations'


class TodoLists(models.Model):
    TodoList_id = models.AutoField(primary_key=True)
    destination = models.CharField(max_length=150, default='')
    todo_list = models.CharField(max_length=500, blank=True, null=True)
    complete_flg = models.BooleanField(null=True)
    create_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)
    update_at = models.DateTimeField(verbose_name="更新日時", auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'todolists'
