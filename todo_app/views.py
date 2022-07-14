# todo_list/todo_app/views.py
from django import forms
from django.forms import Select
from django.http import Http404, HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import ToDoItem, ToDoList, ToDoListShared

from django.template.defaulttags import register

from .utils import date_time
from django.contrib.auth.models import User
from django.db.models import Q

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)

class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)

class ListListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = ToDoList
    template_name = "todo_app/index.html"

    def get_queryset(self):
        return ToDoList.objects.filter(username=self.request.user)

    def get_context_data(self):
        context = super(ListListView, self).get_context_data()
        context["list_x_item_count"] = {}
        for l in ToDoList.objects.all():
            context["list_x_item_count"][l.id] = len(ToDoItem.objects.filter(todo_list_id=l.id))
        
        return context

class ItemListView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = ToDoItem
    template_name = "todo_app/todo_list.html"

    def get_queryset(self):
        if ToDoList.objects.get(id=self.kwargs["list_id"]).username != self.request.user:
            raise Http404
        else:
            return ToDoItem.objects.filter(todo_list_id=self.kwargs["list_id"])

    def get_context_data(self):
        context = super().get_context_data()
        context["todo_list"] = ToDoList.objects.get(id=self.kwargs["list_id"])
        return context

class ListCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = ToDoList
    fields = ["title"]

    def form_valid(self, form): # new
        form.instance.username = self.request.user
        return super().form_valid(form)

    def get_context_data(self):
        context = super(ListCreate, self).get_context_data()
        context["title"] = "Add a new ToDo list"
        return context

class ItemCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
    ]

    def get_form(self):
        '''add date picker in forms'''
        form = super(ItemCreate, self).get_form()
        form.fields['due_date'].widget = date_time.DateTimeLocalField().widget
        form.fields['todo_list'].queryset = ToDoList.objects.filter(username=self.request.user)
        return form

    def form_valid(self, form): # new
        form.instance.username = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        initial_data = super(ItemCreate, self).get_initial()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        initial_data["todo_list"] = todo_list
        return initial_data

    def get_context_data(self):
        context = super(ItemCreate, self).get_context_data()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        context["todo_list"] = todo_list
        context["title"] = "Create a new ToDo"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])

class ItemUpdate(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
    ]

    def get_form(self):
        '''add date picker in forms'''
        form = super(UpdateView, self).get_form()
        form.fields['due_date'].widget = date_time.DateTimeLocalField().widget
        form.fields['todo_list'].queryset = ToDoList.objects.filter(username=self.request.user)
        return form

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ItemUpdate, self).get_object()
        if not obj.username == self.request.user:
            raise Http404
        return obj

    def get_context_data(self):
        context = super(ItemUpdate, self).get_context_data()
        context["todo_list"] = self.object.todo_list
        context["title"] = "Edit ToDo"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])

class ListDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = ToDoList
    # You have to use reverse_lazy() instead of reverse(),
    # as the urls are not loaded when the file is imported.
    success_url = reverse_lazy("index")

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ListDelete, self).get_object()
        if not obj.username == self.request.user:
            raise Http404
        return obj

class ItemDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = ToDoItem

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ItemDelete, self).get_object()
        if not obj.username == self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        return reverse_lazy("list", args=[self.kwargs["list_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todo_list"] = self.object.todo_list
        return context

######### sharing content #########
class ListSharedCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = ToDoListShared
    fields = [
        "todo_list",
        "username_consumer",
    ]

    def get_form(self):
        '''add date picker in forms'''
        form = super(CreateView, self).get_form()
        form.fields['todo_list'].queryset = ToDoList.objects.filter(username=self.request.user)
        form.fields['username_consumer'] = forms.ChoiceField(choices=
            ((c.id, c) for c in User.objects.filter(~Q(id=self.request.user.id)))
        )
        return form
    
    def form_valid(self, form): # new
        form.instance.username_sharer = self.request.user.id
        return super().form_valid(form)
    
    def get_context_data(self):
        context = super(CreateView, self).get_context_data()
        context["title"] = "Share a ToDo List"
        return context
    
    def get_initial(self):
        initial_data = super(CreateView, self).get_initial()
        todo_list = ToDoList.objects.filter(username=self.request.user).first()
        initial_data["todo_list"] = todo_list
        return initial_data
    
    def get_success_url(self):
        return reverse_lazy("index")