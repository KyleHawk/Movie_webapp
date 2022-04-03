from django.contrib import admin
from .models import Writer, Cast, Movie, SoundSection, Director, Producer, Genre, Musician, User
# Register your models here.
admin.site.register(Writer)
admin.site.register(Cast)
admin.site.register(Movie)
admin.site.register(SoundSection)
admin.site.register(Director)
admin.site.register(Producer)
admin.site.register(Genre)
admin.site.register(Musician)
admin.site.register(User)
