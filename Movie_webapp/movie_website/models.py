from django.db import models
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.validators import MaxValueValidator


# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    c_time = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatar', default='', verbose_name='avatar')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "user"
        verbose_name_plural = "user"


class Writer(models.Model):
    name = models.CharField(max_length=300, verbose_name='Writer_name')

    def __str__(self):
        return self.name


class SoundSection(models.Model):
    artist_name = models.CharField(max_length=300, db_index=True)
    artist_type = models.CharField(max_length=300)

    def __str__(self):
        return self.artist_name + ' : ' + self.artist_type


class Cast(models.Model):
    name = models.CharField(max_length=400, verbose_name='Cast_name')

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=400, verbose_name='Director_name')

    def __str__(self):
        return self.name


class Producer(models.Model):
    name = models.CharField(max_length=400, verbose_name='Producer_name')

    def __str__(self):
        return self.name


class Musician(models.Model):
    name = models.CharField(max_length=400, verbose_name='Musician_name')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=400, verbose_name='Genre_name')

    def __str__(self):
        return self.name


class Movie(models.Model):
    # page one features
    title = models.CharField(max_length=200, verbose_name='Movie Title')
    description = models.CharField(max_length=500, verbose_name='Description')
    rating = models.DecimalField(max_length=500, decimal_places=2, max_digits=4, verbose_name='Rating')
    # page two features
    image_url = models.CharField(max_length=1000, verbose_name='Image Link', default='')
    duration = models.CharField(max_length=200, verbose_name='Duration')
    year = models.CharField(max_length=500, verbose_name='Year')
    writers = models.ManyToManyField(Writer)
    director = models.ManyToManyField(Director)
    producer = models.ManyToManyField(Producer)
    cast = models.ManyToManyField(Cast)
    sounds = models.ManyToManyField(SoundSection, blank=True)
    musician = models.ManyToManyField(Musician)
    genre = models.ManyToManyField(Genre)
    number = models.IntegerField(default=100,verbose_name='Total Number of Rating')
    latest = models.PositiveIntegerField(validators=[MaxValueValidator(10)], null=True, verbose_name='Latest User Rating')

    def __str__(self):
        return self.title


class Orders(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    movie_name = models.CharField(max_length=100, verbose_name='Movie Name')
    order_date = models.DateField()
    order_status = models.CharField(max_length=100,verbose_name='status')
