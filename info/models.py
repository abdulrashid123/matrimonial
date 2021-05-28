from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.shortcuts import redirect
import os


class User(AbstractUser):
    email = models.EmailField(verbose_name='email address',max_length=255,unique=True,blank=True,null=True)
    mobile_no = models.CharField(validators=[
        RegexValidator(
            regex='[1-9]{1}[0-9]{9}',
            message='Number should be 10 digit',
            code='invalid_number'
        ),
    ],max_length=10,blank=True,null=True)
    full_name = models.CharField(max_length=255,blank=True,null=True)
    relation = models.CharField(max_length=10,blank=True,null=True)
    gender = models.CharField(max_length=6,blank=True,null=True)
    profile_active = models.BooleanField(default=False)

    def profile_active_url(self):
        return redirect('info:home')


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,blank=True,null=True,on_delete=models.CASCADE,related_name='profile')
    age = models.PositiveSmallIntegerField(blank=True,null=True)
    requested = models.ManyToManyField(User,blank=True,related_name='request')
    # Bride grooms details
    navaras = models.CharField(max_length=50,blank=True,null=True)
    maritial_status = models.CharField(max_length=50,blank=True,null=True)
    height = models.FloatField(blank=True,null=True)
    weight = models.PositiveSmallIntegerField(blank=True,null=True)
    body_type = models.CharField(max_length=20,blank=True,null=True)
    birthdate = models.DateField(blank=True,null=True)
    blood_group = models.CharField(max_length=10,blank=True,null=True)
    mother_tongue = models.CharField(max_length=30,blank=True,null=True)
    annual_income = models.CharField(max_length=20,blank=True,null=True)
    religion = models.CharField(max_length=30,null=True,blank=True)
    caste = models.CharField(max_length=20,null=True,blank=True)
    sub_caste = models.CharField(max_length=20,blank=True,null=True)
    birthplace = models.CharField(max_length=50,blank=True,null=True)
    occupation = models.CharField(max_length=100,blank=True,null=True)
    occupation_detail = models.CharField(max_length=200,blank=True,null=True)
    education = models.CharField(max_length=100,blank=True,null=True)
    education_detail = models.CharField(max_length=200,blank=True,null=True)

    drink_habit = models.CharField(max_length=20,blank=True,null=True)
    smoke_habit = models.CharField(max_length=20,blank=True,null=True)
    eating_habits = models.CharField(max_length=100,blank=True,null=True)
    hobbies = models.CharField(max_length=100,blank=True,null=True)

    devak = models.CharField(max_length=100,blank=True,null=True)
    mana = models.CharField(max_length=100,blank=True,null=True)
    nadi = models.CharField(max_length=100,blank=True,null=True)
    rassi = models.CharField(max_length=100,blank=True,null=True)

    father_name = models.CharField(max_length=100,blank=True,null=True)
    father_occupation = models.CharField(max_length=200,blank=True,null=True)
    mother_name = models.CharField(max_length=100,blank=True,null=True)
    brother_count = models.PositiveSmallIntegerField(default=0)
    sister_count = models.PositiveSmallIntegerField(default=0)
    uncle_count = models.PositiveSmallIntegerField(default=0)
    atya_count = models.PositiveSmallIntegerField(default=0)
    mavasi_count = models.PositiveSmallIntegerField(default=0)
    other_relatives = models.CharField(max_length=100,blank=True,null=True)

    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=100,blank=True,null=True)
    city = models.CharField(max_length=100)
    zipcode = models.PositiveIntegerField()
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    current_location = models.CharField(max_length=200)
    views = models.IntegerField(default=0)
    expectations = models.CharField(max_length=200,blank=True,null=True)
    paid = models.BooleanField(default=False)
    agree_tnc = models.BooleanField()

    class Meta:
        ordering = ['views']

    def __str__(self):
        return self.user.username
def user_directory_path(instance,filename):

    return f'post/{instance.user.username}/{filename}'

def payment_file_path(instance,filename):
    return f'payment/{instance.user.username}/{filename}'


class Payment(models.Model):
    user = models.OneToOneField(User,blank=True,null=True,related_name='payment',on_delete=models.CASCADE)
    image = models.FileField(upload_to=payment_file_path, blank=True, null=True)

    def __str__(self):
        return self.user.username

class ProfileImage(models.Model):
    user = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE,related_name="img")
    image = models.ImageField(upload_to=user_directory_path,blank=True,null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save,sender=Profile)
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        u = User.objects.get(pk=instance.user.id)
        u.profile_active = True
        u.save()


def _delete_files(path):
    if os.path.isfile(path):
        os.remove(path)


@receiver(models.signals.post_delete, sender=ProfileImage)
def delete_file(sender, instance, *args, **kwargs):
    if instance.image:
        _delete_files(instance.image.path)

@receiver(post_delete, sender=Profile)
def set_flag(sender, instance, *args, **kwargs):
    try:
        u = User.objects.get(pk=instance.user.id)
        u.profile_active = False
        u.save()
    except:
        pass


