import random
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from . import models
from . import forms
import logging
import threading
import datetime
import requests
import json
from django.shortcuts import get_object_or_404
from .models import Movie, Orders, User, Genre, Director, Cast, Writer
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from movie_project.settings import EMAIL_HOST_USER
import decimal


def index(request):
    # 如果登陆了就显示用户名，不然就显示Login
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'
    movie_list = Movie.objects.all()
    return render(request, 'login/index.html', {'movie_list': movie_list})


def login(request):
    # 不允许重复登陆
    if request.session.get('is_login', None):
        return redirect('/')
    if request.method == "POST":
        # 实例
        login_form = forms.UserForm(request.POST)
        message = 'Check your username or password'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = models.User.objects.get(name=username)
            except:
                message = 'User does not exist!'
                # 使用locals代替{'message': message}
                return render(request, 'login/login.html', locals())

            if user.password == password:
                # 可以往里面写任何数据，不限于用户相关
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                # request.session.set_expiry()
                return redirect('/index/')
            else:
                message = 'Password incorrect'
                return render(request, 'login/login.html', locals())

        else:
            return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "Check your input！"
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')

            if password1 != password2:
                message = 'Wrong password'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = 'Username already exists'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = 'Email already exists！'
                    return render(request, 'login/register.html', locals())

                new_user = models.User()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.save()

                return redirect('/login/')
        else:
            return render(request, 'login/register.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")

def check_db(name):
    result = True
    try:
        res = Movie.objects.get(title=name)
    except ObjectDoesNotExist:
        result = False
    return result


def check_presence(type, name):
    result = None
    try:
        result = type.objects.get(name=name)
    except ObjectDoesNotExist:
        result = None
    return result


def get_movie(title):
    url = "http://www.omdbapi.com/?apikey=40024d7d&"

    querystring = {"t": str(title)}

    response = requests.request("GET", url, params=querystring)

    return response.text


def fetch_and_store(title, user_id):
    movie_data = get_movie(title)
    logger = logging.getLogger(__name__)
    json_data = json.loads(movie_data)
    logger.info(json_data)
    movie = Movie()
    movie.title = json_data['Title']
    movie.description = json_data['Plot']
    movie.duration = json_data['Runtime']
    movie.image_url = json_data['Poster']
    movie.rating = json_data['imdbRating']
    movie.year = str(json_data['Released'])[-4:]
    movie.save()
    res = check_presence(Director, json_data['Director'])
    if res is None:
        direct = Director()
        direct.name = json_data['Director']
        direct.save()
        movie.director.add(direct)
    else:
        movie.director.add(res)
    genres = str(json_data['Genre']).split(', ')
    for genre_name in genres:
        res = check_presence(Genre, genre_name)
        if res is None:
            gen = Genre()
            gen.name = genre_name
            gen.save()
            movie.genre.add(gen)
        else:
            movie.genre.add(res)
    writers = str(json_data['Writer']).split(', ')
    for writer_name in writers:
        res = check_presence(Writer, writer_name)
        if res is None:
            writ = Writer()
            writ.name = writer_name
            writ.save()
            movie.writers.add(writ)
        else:
            movie.writers.add(res)
    cast_names = str(json_data['Actors']).split(', ')
    for cast_name in cast_names:
        res = check_presence(Cast, cast_name)
        if res is None:
            actor = Cast()
            actor.name = cast_name
            actor.save()
            movie.cast.add(actor)
        else:
            movie.cast.add(res)
    order = Orders.objects.get(user_id=user_id, movie_name=movie.title)
    order.order_status = "Completed";
    order.save()


def place_order(request):
    if request.session.get('is_login', None):
        if request.method == 'POST':
            order_form = forms.OrderMovieForm(request.POST)
            if order_form.is_valid():
                title = order_form.cleaned_data.get('title')
                if check_db(title):
                    message = "unsuccess"
                    return render(request, 'login/status.html', locals())
                else:
                    order = Orders()
                    usr_id = request.session['user_id']
                    order.user_id = User.objects.get(id=usr_id)
                    order.order_status = "In Progress"
                    order.order_date = datetime.date.today()
                    order.movie_name = title
                    order.save()
                    message = "success"
                    fetch = threading.Thread(target=fetch_and_store(title, usr_id), args=(1,))
                    fetch.start()
                    return render(request, 'login/status.html', locals())

        order_form = forms.OrderMovieForm()
        return render(request, 'login/order.html', locals())


def order_status(request):
    if request.session.get('is_login', None):
        usr_id = request.session['user_id']
        orders = Orders.objects.filter(user_id=usr_id)
        return render(request, 'login/order_status.html', locals())

def detail(request, movie_no):
    # remain the state
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'

    movie = get_object_or_404(Movie, id=movie_no)
    return render(request, 'login/detail.html', locals())


def action_filter(request):
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'
    movie_list = Movie.objects.filter(genre__name='Action')
    return render(request, 'login/index.html', {'movie_list': movie_list})


def crime_filter(request):
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'
    movie_list = Movie.objects.filter(genre__name='Crime')
    return render(request, 'login/index.html', {'movie_list': movie_list})


def fantasy_filter(request):
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'
    movie_list = Movie.objects.filter(genre__name='Fantasy')
    return render(request, 'login/index.html', {'movie_list': movie_list})


def drama_filter(request):
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'
    movie_list = Movie.objects.filter(genre__name='Drama')
    return render(request, 'login/index.html', {'movie_list': movie_list})


def top_10(request):
    if request.session.get('is_login', None):
        username = request.session['user_name']
    else:
        username = 'Login'
    movie_list = Movie.objects.all().order_by('-rating')[:10]
    return render(request, 'login/index.html', {'movie_list': movie_list})


def upload(request):
    if request.session.get('is_login', None):
        if request.method == 'POST' and request.FILES['upload']:
            upload = request.FILES['upload']
            fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
            models.User.objects.filter(name=request.session['user_name']).update(avatar=file_url)
            return render(request, 'login/up1.html', {'file_url': file_url})
        return render(request, 'login/up1.html')
    else:
        return redirect("/login/")



#发送邮件找回密码
def findpwdView(request):
    if request.method == 'POST':
        username=request.POST.get("username")
        email=request.POST.get("email")
        subject='New password'
        # new password random string
        H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        new_pwd = ''
        for i in range(10):
            new_pwd += random.choice(H)
        message = 'Your new password is: ' + new_pwd
        send_mail(subject,message, EMAIL_HOST_USER, [email], fail_silently=False)
        user = models.User.objects.get(name=username)
        user.password = new_pwd
        user.save()

        return render(request, 'login/success.html', {'email': email})
    return render(request, 'login/index.html')

def forgotPwd(request):
    return render(request, 'login/findpwd.html')


def rating(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        num = request.POST.get('num')
        movie = Movie.objects.get(id=id)
        movie.latest = num
        movie.rating = (movie.rating * movie.number + decimal.Decimal(num))/(movie.number + 1)
        movie.number = movie.number + 1
        movie.save()
    return JsonResponse({'success':'true', 'score': num}, safe=False)
    return JsonResponse({'success':'false'})
