

from django.urls import path,re_path
from crm import views

urlpatterns = [
    re_path('^$', views.index,name="sales_index"),
    re_path('^customers/$',views.customer_list,name="customer_list"),
    re_path(r'customer/(\d+)/enrollment/$', views.enrollment, name="enrollment"),
    re_path(r'customer/registration/(\d+)/(\w+)/$',views.register,name="register"),
    re_path(r'registration_confirm/(\d+)/$',views.registration_confirm,name="registration_confirm"),
    re_path(r'registration_refuse/(\d+)/$',views.registration_refuse,name="registration_refuse"),
    re_path(r'payment/(\d+)/$',views.payment,name="payment")

]
