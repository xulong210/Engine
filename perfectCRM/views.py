from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
# Create your views here.

def account_login(request):
    errors = {}
    if request.method == "POST":
        _email = request.POST.get("email")
        _password = request.POST.get("password")
        user = authenticate(username=_email,password=_password)
        #如果账号密码正确 user返回用户名对象 如果错误 返回None
        if user:
            login(request,user)
            next_url = request.GET.get("next","/crm/")
            return redirect(next_url)
        else:
            errors['error'] = "Wrong username or password"
    return render(request,"login.html",{"errors":errors})

def account_logout(request):
    logout(request)
    return redirect("/accounts/login/")