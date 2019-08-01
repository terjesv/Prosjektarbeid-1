from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from website.forms import RegistrationForm


def login_view(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
        else:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
            elif User.objects.filter(username=username).exists():
                messages.add_message(request, messages.ERROR, 'Incorrect password')
            else:
                messages.add_message(request, messages.ERROR, 'Username does not exist')
        return HttpResponseRedirect(reverse('post_list'))


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if not User.objects.filter(username=request.POST['username']).exists():
            user = form.save()
            user.set_password(request.POST['password'])
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('post_list'))
        else:
            messages.add_message(request, messages.ERROR, 'Username is already taken')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', None))
    else:
        form = RegistrationForm()
        return render(request, 'registration/registration_form.html', {'form': form})
