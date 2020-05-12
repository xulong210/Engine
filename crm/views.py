from django.shortcuts import render,HttpResponse,redirect
from crm import forms,models
# Create your views here.
from django.db import IntegrityError
import random,string
from django.core.cache import cache
import os
from perfectCRM import settings

def index(request):

    return render(request,"index.html")

def customer_list(request):
    return render(request,"sales/customers.html")


def enrollment(request,obj_id):
    obj = models.Customer.objects.get(id=obj_id)
    msg = {}
    if request.method == "POST":
        enroll_form = forms.EnrollmentForm(request.POST)
        if enroll_form.is_valid():
            print(enroll_form.cleaned_data)
            message = '''请将此连接发送欸客户:
                            http://127.0.0.1:8080/crm/customer/registration/{enroll_obj_id}/{random_str}'''
            random_str = ''.join(random.sample(string.ascii_lowercase+string.digits,6))
            try:
                enroll_form.cleaned_data["customer"] = obj
                enroll_obj = models.Enrollment.objects.create(**enroll_form.cleaned_data)
                message = message.format(enroll_obj_id=enroll_obj.id,random_str=random_str)
                msg["msg"] = message
            except IntegrityError as e:
                enroll_obj = models.Enrollment.objects.get(customer_id=obj_id,enrolled_class_id=enroll_form.cleaned_data["enrolled_class"].id)
                if enroll_obj.contract_agreed:
                    return redirect("/crm/registration_confirm/%s/"%enroll_obj.id)
                enroll_form.add_error("__all__","该用户已报名此班级")
                message = message.format(enroll_obj_id=enroll_obj.id,random_str=random_str)
                msg["msg"] = message
            cache.set(enroll_obj.id,random_str,3000)
    else:
        enroll_form = forms.EnrollmentForm()
    return render(request,"sales/enrollment.html",{"form_obj":enroll_form,"obj":obj,"msg":msg})


def register(request,enroll_id,random_str):
    if cache.get(enroll_id) == random_str:
        enroll_obj = models.Enrollment.objects.get(id=enroll_id)
        status = False
        if request.method == "POST":

            if request.is_ajax():
                print("ajax post, ", request.FILES)
                enroll_data_dir = "%s/%s" %(settings.ENROLLED_DATA,enroll_id)
                if not os.path.exists(enroll_data_dir):
                    os.makedirs(enroll_data_dir,exist_ok=True)

                for k,file_obj in request.FILES.items():
                    with open("%s/%s"%(enroll_data_dir, file_obj.name), "wb") as f:
                        for chunk in file_obj.chunks():
                            f.write(chunk)
                return HttpResponse("success")
            else:
                customer_form = forms.CustomerForm(request.POST,instance=enroll_obj.customer)
                if customer_form.is_valid():
                    customer_form.save()
                    enroll_obj.contract_agreed = True
                    enroll_obj.save()
                    status = True
                    return render(request,"sales/register.html",{"status":status})
        else:
            if enroll_obj.contract_agreed == True:
                status = True
            customer_form = forms.CustomerForm(instance=enroll_obj.customer)
    else:
        return HttpResponse("该链接已过期 抱歉！")
    return render(request,"sales/register.html",{"customer_form":customer_form,"enroll_obj":enroll_obj,"status":status})


def registration_confirm(request,enroll_id):
    #需要显示客户信息 和 选课信息
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)

    return render(request,"sales/registration_confirm.html",{"enroll_obj":enroll_obj,
                                                             "customer_form":customer_form})

def registration_refuse(request,enroll_id):
    #驳回客户报名 返回到报名页面
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()

    return redirect("/crm/customer/%s/enrollment/"%enroll_id)


def payment(request,enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    errors = {}
    if request.method == "POST":
        amount = request.POST.get("amount")
        if amount:
            amount = int(amount)
            if amount <= 500:
                errors["error"] = "此费用不能低于500"
            else:
                models.Payment.objects.create(
                    customer=enroll_obj.customer,
                    course=enroll_obj.enrolled_class.course,
                    amount=amount,
                    consultant=enroll_obj.consultant
                )
                enroll_obj.customer.status = 0
                enroll_obj.customer.save()

                return redirect("/king_admin/crm/Customer/")
        else:
            errors["error"] = "费用不能为空"
    else:
        enroll_obj.contract_approval = True
        enroll_obj.save()
    return render(request,"sales/payment.html",{"enroll_obj":enroll_obj,
                                                "errors":errors})