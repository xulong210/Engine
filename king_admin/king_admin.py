#__author:"xulong"
#date:   2020/1/19

from crm import models
from django.shortcuts import render,redirect,HttpResponse

# {'crm':{'Customer':CustomerAdmin,'CustomerFollowUp':CustomerFollowUpAdmin}}
enabled_admins = {}
class BaseAdmin(object):
    list_display = []
    list_filters = []
    list_per_page = 5
    search_fields = []
    filter_horizontal = []
    actions = ["delete_selected_objs",]
    readonly_fields = []
    table_readonly = False
    modelform_exclude_fields = []
    def delete_selected_objs(self,request,querySets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.object_name
        errors = {}
        if request.method =="POST":
            if not self.table_readonly:
                if request.POST.get("sub") == "del":
                    querySets.delete()
                    return redirect("/king_admin/%s/%s" % (app_name, table_name))
                elif request.POST.get("sub") == "return":
                    return redirect("/king_admin/%s/%s" % (app_name, table_name))
            errors = {"__all__":"table_readonly,connot be deleted"}
        selected_ids = ",".join([str(i.id) for i in querySets])
        return render(request,"king_admin/table_obj_delete.html",{"objs":querySets,
                                                                  "admin_class":self,
                                                                  "app_name":app_name,
                                                                  "table_name":table_name,
                                                                  "selected_ids":selected_ids,
                                                                  "action":request._admin_action,
                                                                  "errors":errors})

    delete_selected_objs.display_name = "删除选中信息"

    def default_form_validation(self):
        '''用户可以在此进行自定义的表单验证，相当于Django form的clean方法'''
        pass

class CustomerAdmin(BaseAdmin):
    list_display = ['id','qq','name','source','consultant','consult_course','date','status','enroll']
    list_filters = ['source','consultant','consult_course','status','date']
    search_fields = ['qq','name','consultant__name']
    filter_horizontal = ['tags',]
    readonly_fields = ['qq','consultant','tags']
    #table_readonly = True
    #CustomerAdmin.model = model.Customer
    def default_form_validation(self):
        #print("---cutomer validation---",self)
        #print("---instance---",self.instance)
        print("---cleaned_data---",self.cleaned_data)
        consult_content = self.cleaned_data.get("content","")
        if len(consult_content) < 15:
            return self.ValidationError(
                ('Field %(field)s 咨询内容记录不能少于15个字符'),
                code='invalid',
                params={'field':'content',}
            )

    def clean_name(self):
        print("name clean validation:",self.cleaned_data["name"])
        data = self.cleaned_data["name"]
        if not data:
            self.add_error("name","connot be null")
        return data

    def enroll(self):
        if self.instance.status == 0:
            field_name = "报名新课程"
        else:
            field_name = "报名"
        return '''<a href="/crm/customer/%s/enrollment/">%s</a>'''% (self.instance.id,field_name)
class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer','consultant','date']



class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class','day_num','teacher']

    def create_all_study_record(self,request,querySets):
        if len(querySets)>1:
            return HttpResponse("不能同时创建超过1个班级的上课记录")
        create_obj_list = []
        print("--------------",querySets[0].from_class.enrollment_set.all())
        for enroll_obj in querySets[0].from_class.enrollment_set.all():
            create_obj_list.append(models.StudyRecord(
                student = enroll_obj,
                course_record = querySets[0],
                attendance = 0,
                score = 0,
            ))
        try:
            models.StudyRecord.objects.bulk_create(create_obj_list)
        except Exception as e:
            return HttpResponse("批量初始化学习记录失败 请检查该节课是否已经有对应的学习记录")
        return redirect('/king_admin/crm/StudyRecord/?course_record=%s'%(querySets[0].id))
    create_all_study_record.display_name = "初始化本节课所有学员上课记录"
    actions = ['create_all_study_record',]

class StudyRecordAdmin(BaseAdmin):
    list_display = ['student','course_record','attendance','score']
    list_filters = ['course_record','attendance']


class UserProfileAdmin(BaseAdmin):
    list_display = ['id','email','name','is_active','is_admin']
    readonly_fields = ['password',]
    filter_horizontal = ['user_permissions','groups']
    modelform_exclude_fields = ['last_login',]

def register(model_class,admin_class=None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}
    admin_class.model = model_class #绑定model对象和Admin model_class即表=如models.Customer
    enabled_admins[model_class._meta.app_label][model_class._meta.object_name] = admin_class
    #enabled_admins[app名][model表名]

register(models.Customer,CustomerAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.UserProfile,UserProfileAdmin)
register(models.CourseRecord,CourseRecordAdmin)
register(models.StudyRecord,StudyRecordAdmin)