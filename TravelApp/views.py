from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import TemplateView, View
from .forms import RegistForm, UserLoginForm, TravelRecordInsertForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from . import forms
from .models import Destinations, TodoLists
from django.core.files.storage import FileSystemStorage
import os
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError

class HomeView(TemplateView):
    template_name = 'home.html'

class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm
'''
class UserLoginView(FormView):
    template_name = 'user_login.html'
    form_class = UserLoginForm

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        next_url = request.POST['next']
        if user is not None and user.is_active:
            login(request, user)
        if next_url:
            return redirect(next_url)
        return redirect('TravelApp:home')
'''
class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm
    
class UserLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('TravelApp:user_login')


#ログインしてなくてもユーザー画面が見れてしまう
#class UserView(TemplateView):
#    template_name = 'user.html'


# @method_decorator(login_required, name='dispatch')
class UserView(LoginRequiredMixin, TemplateView):
    template_name = 'user.html'

    # @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


###ユーザー情報、パスワード変更###
@login_required
def user_edit(request):
    user_edit_form = forms.UserEditForm(request.POST or None, instance=request.user)
    if user_edit_form.is_valid():
        messages.success(request, '更新完了しました。')
        user_edit_form.save()
    return render(request, 'user_edit.html', context={
        'user_edit_form': user_edit_form,
    })

@login_required
def change_password(request):
    password_change_form = forms.PasswordChangeForm(request.POST or None, instance=request.user)
    if password_change_form.is_valid():
        try:
            password_change_form.save()
            messages.success(request, 'パスワード更新完了しました。')
            update_session_auth_hash(request, request.user)
        except ValidationError as e:
            password_change_form.add_error('password', e)
    return render(
        request, 'change_password.html', context={
            'password_change_form': password_change_form,
        }
    )

###旅行記録登録、編集、削除###
def insert_TravelRecord(request):
    insert_form = forms.TravelRecordInsertForm(request.POST or None, request.FILES or None)
    if insert_form.is_valid():
        insert_form.save()
        insert_form = forms.TravelRecordInsertForm()
    return render(
        request, 'insert_TravelRecord.html', context={
            'insert_form': insert_form
        }
    )

def destinations_list(request):
    destinations = Destinations.objects.all()
    return render(
        request, 'destinations_list.html', context={
            'destinations': destinations
        }
    )

def update_destination(request, destination_id):
    destination = Destinations.objects.get(destination_id=destination_id)
    update_form = forms.DestinationUpdateForm(
        initial = {
            'destination_id': destination.destination_id, 'destination_name': destination.destination_name, 'date': destination.date, 'TravelRecord': destination.TravelRecord, 'picture': destination.picture
        }
    )
    if request.method == 'POST':
        
        update_form = forms.DestinationUpdateForm(request.POST or None, request.FILES or None)
        if update_form.is_valid():
            destination.destination_name = update_form.cleaned_data['destination_name']
            destination.date = update_form.cleaned_data['date']
            destination.TravelRecord = update_form.cleaned_data['TravelRecord']         
            picture = update_form.cleaned_data['picture']
            if picture:
                fs = FileSystemStorage()
                file_name = fs.save(os.path.join('destination', picture.name), picture)
                destination.picture = file_name
            destination.save()
        

    return render(
        request, 'update_destination.html', context={
            'update_form': update_form,
            'destination': destination
        }
    )

def delete_destination(request, destination_id):
    delete_form = forms.DestinationDeleteForm(
        initial={
            'destination_id': destination_id
        }
    )
    if request.method == 'POST':
        delete_form = forms.DestinationDeleteForm(request.POST or None)
        if delete_form.is_valid():
            Destinations.objects.get(destination_id=delete_form.cleaned_data['destination_id']).delete()
    return render(
        request, 'delete_destination.html', context={
            'delete_form': delete_form
        }
    )

###ToDoリスト登録、編集、削除###
class TodoView(TemplateView):
    template_name = 'Todo.html'

def insert_TodoList(request):
    insert_form = forms.TodoListInsertForm(request.POST or None)
    if insert_form.is_valid():
        insert_form.save()
        insert_form = forms.TodoListInsertForm()
    return render(
        request, 'insert_TodoList.html', context={
            'insert_form': insert_form
        }
    )


def Todo_List(request):
    todolists = TodoLists.objects.all()
    return render(
        request, 'Todo_List.html', context={
            'todolists': todolists
        }
    )

def update_TodoList(request, TodoList_id):
    todolist = TodoLists.objects.get(TodoList_id=TodoList_id)
    update_form = forms.TodoListUpdateForm(
        initial = {
            'TodoList_id': todolist.TodoList_id, 'destination': todolist.destination, 'todo_list': todolist.todo_list, 'complete_flg': todolist.complete_flg
        }
    )
    if request.method == 'POST':
        
        update_form = forms.TodoListUpdateForm(request.POST or None)
        if update_form.is_valid():
            todolist.destination = update_form.cleaned_data['destination']
            todolist.todo_list = update_form.cleaned_data['todo_list']
            todolist.complete_flg = update_form.cleaned_data['complete_flg']         
            #picture = update_form.cleaned_data['picture']
            #if picture:
            #    fs = FileSystemStorage()
            #    file_name = fs.save(os.path.join('destination', picture.name), picture)
            #    destination.picture = file_name
            #destination.save()
        
    return render(
        request, 'update_TodoList.html', context={
            'update_form': update_form,
            'todolist': todolist
        }
    )

def delete_TodoList(request, TodoList_id):
    delete_form = forms.TodoListDeleteForm(
        initial={
            'TodoList_id': TodoList_id
        }
    )
    if request.method == 'POST':
        delete_form = forms.TodoListDeleteForm(request.POST or None)
        if delete_form.is_valid():
            TodoLists.objects.get(TodoList_id=delete_form.cleaned_data['TodoList_id']).delete()
    return render(
        request, 'delete_TodoList.html', context={
            'delete_form': delete_form
        }
    )
