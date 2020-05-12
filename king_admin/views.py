from django.shortcuts import render,redirect

# Create your views here.
from king_admin import king_admin
from king_admin.utils import table_filter,table_sort,table_search
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from king_admin.forms import create_model_form
import re
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, "king_admin/table_index.html",{"table_list":king_admin.enabled_admins})

@login_required
def display_table_objs(request,app_name,table_name):
    # model_module = importlib.import_module("%s.models"%(app_name))
    # model_obj = getattr(model_module,table_name)
    #print(model_obj.__dict__)
    print("-->",app_name,table_name)

    admin_class = king_admin.enabled_admins[app_name][table_name]
    if request.method == "POST":
        ids_list = request.POST.get("selected_ids").split(",")
        #print(ids_list)
        action = request.POST.get("action")
        querySets = admin_class.model.objects.filter(id__in=[int(id) for id in ids_list])
        if hasattr(admin_class,action):
            action_func = getattr(admin_class,action)
            request._admin_action = action
            return action_func(admin_class,request,querySets)

    object_list,filter_conditions =table_filter(request,admin_class) #过滤后的结果

    object_list = table_search(request,admin_class,object_list) #关键字查询结果

    object_list,orderby_key = table_sort(request,admin_class,object_list) #排序后的查询集

    paginator = Paginator(object_list,admin_class.list_per_page)
    #获取分页对象

    page = request.GET.get("page") #获取当前或者请求页面的页码
    try:
        query_sets = paginator.page(page) #获取这一页被分配的数据
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_sets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_sets = paginator.page(paginator.num_pages) #num_pages是总页数
    return render(request,"king_admin/table_objs.html",{"admin_class":admin_class,
                                                        "filter_conditions":filter_conditions,
                                                        'query_sets':query_sets,
                                                        "orderby_key":orderby_key,
                                                        "search_key":request.GET.get("_q","")})

@login_required
def table_obj_change(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(request, admin_class)
    model_obj = admin_class.model.objects.get(id=obj_id)
    if request.method == "POST":
        form_obj = model_form_class(request.POST,instance=model_obj)
        if form_obj.is_valid():
            form_obj.save()
    else:
        form_obj = model_form_class(instance=model_obj)
    return render(request,"king_admin/table_obj_change.html",{"form_obj":form_obj,
                                                              "admin_class":admin_class,
                                                              "app_name":app_name,
                                                              "table_name":table_name})

@login_required
def table_obj_add(request,app_name,table_name):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    admin_class._add_form = True
    model_form_class = create_model_form(request,admin_class)
    if request.method == "POST":
        form_obj = model_form_class(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(request.path.replace('/add/','/'))
    else:
        form_obj = model_form_class()
    return render(request,"king_admin/table_obj_add.html",{"form_obj":form_obj,
                                                           "admin_class":admin_class,
                                                           "app_name":app_name,
                                                           "table_name":table_name})

@login_required
def table_obj_delete(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)
    obj_list = []
    obj_list.append(obj)
    errors = {}
    if request.method == "POST":
        if not admin_class.table_readonly:
            if request.POST.get("sub") == "del":
                admin_class.model.objects.filter(id=obj_id).delete()
                return redirect("/king_admin/%s/%s" % (app_name, table_name))
            elif request.POST.get("sub") == "return":
                return redirect(request.path.replace('delete','change'))
        errors = {"__all__":"table_readonly,cannot be deleted"}
    return render(request, "king_admin/table_obj_delete.html", {"objs":obj_list,
                                                                "admin_class":admin_class,
                                                                "selected_ids":[obj_id],
                                                                "action":"",
                                                                "errors":errors})

@login_required
def password_reset(request,app_name,table_name,obj_id):
    admin_class = king_admin.enabled_admins[app_name][table_name]

    obj = admin_class.model.objects.get(id=obj_id)
    errors = {}
    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1 == password2:
            if len(password1)>5:
                res = re.search("\d+",password1)
                if res and res.group() != password1 and \
                    "".join(re.findall("[a-z]",password1)) != password1:
                    obj.set_password(password1)
                    obj.save()
                    return redirect(request.path.rstrip("password/"))
                else:
                    errors['invalid_password'] = "密码必须包含英文字母和数字"
            else:
                errors['invalid_password'] = "密码长度小于6"
        else:
            errors['invalid_password'] = "两次输入密码不一致"

    return render(request,"king_admin/password_reset.html",{'obj':obj,'errors':errors})



