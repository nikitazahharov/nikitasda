from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'comapp/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'comapp/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currentses')
            except IntegrityError:
                return render(request, 'comapp/signupuser.html', {'form': UserCreationForm(), 'error': 'Username is already taken'})
        else:
            return render(request, 'comapp/signupuser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match!'})

@login_required
def currentses(request):
    dotask = Task.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-urgent')
    return render(request, 'comapp/currentses.html', {'dotask': dotask})

@login_required
def completedtask(request):
    dotask = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'comapp/completedtask.html', {'dotask': dotask})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'comapp/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return render(request, 'comapp/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username and password did not match'})
        else:
            login(request, user)
            return redirect('home')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtask(request):
    if request.method == 'GET':
        return render(request, 'comapp/createtask.html', {'form': TaskForm()})
    else:
        try:
            form = TaskForm(request.POST)
            newtask = form.save(commit=False)
            newtask.user = request.user
            newtask.save()
            return redirect('currentses')
        except ValueError: 
            return render(request, 'comapp/createtask.html', {'form': TaskForm(), 'error': 'Bad data passed in'})

@login_required
def viewtask(request, task_pk):
    gettask = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'GET':
        form = TaskForm(instance=gettask)
        return render(request, 'comapp/viewtask.html', {'gettask': gettask, 'form': form})
    else:
        try:
            form = TaskForm(request.POST, instance=gettask)
            form.save()
            return redirect('currentses')
        except ValueError:
            return render(request, 'comapp/viewtask.html', {'gettask': gettask, 'form': form, 'error': 'Bad information'})

@login_required
def completetask(request, task_pk):
    gettask = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
         gettask.datecompleted = timezone.now()
         gettask.save()
         return redirect('currentses')

@login_required
def deletetask(request, task_pk):
    gettask = get_object_or_404(Task, pk=task_pk, user=request.user)
    if request.method == 'POST':
        gettask.delete()
        return redirect('currentses')