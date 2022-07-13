from django.urls import path, include
from django.views.generic.base import TemplateView

from django.contrib import admin

admin.autodiscover()

# import hello.views
from todo_app.views import Register

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    #path("", hello.views.index, name="index"),
    #path("db/", hello.views.db, name="db"),
    path("admin/", admin.site.urls),
    path('register/success/',TemplateView.as_view(template_name="registration/success.html"), name ='register-success'),
    path('register/', Register.as_view(), name='register'),
    path('', include('django.contrib.auth.urls')),
    path('', include("todo_app.urls")),
]
