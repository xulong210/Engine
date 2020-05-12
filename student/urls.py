
from django.urls import path,re_path
from student import views

urlpatterns = [
    re_path('^$', views.index,name="stu_index"),
]
