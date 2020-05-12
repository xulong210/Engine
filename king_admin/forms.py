#__author:"xulong"
#date:   2020/1/30
from django.utils.translation import ugettext as _
from django.forms import forms,ModelForm,ValidationError

from crm import models

def create_model_form(request,admin_class):
    '''动态生成Model Form'''

    def __new__(cls,*args,**kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if not hasattr(admin_class,"_add_form"):
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'
            if hasattr(admin_class,"clean_%s"%field_name):
                field_clean_func = getattr(admin_class,"clean_%s"%field_name)
                setattr(cls,"clean_%s"%field_name,field_clean_func)

        return ModelForm.__new__(cls)

    def default_clean(self):
        '''给所有的form默认加一个clean验证'''
        print("---running default clean---",admin_class)
        error_list = []
        if self.instance.id:
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance,field)
                if hasattr(field_val,"select_related"): #对多对多tags的判断
                    query_list = field_val.select_related()
                    set_val = set(query_list)
                    set_val_from_front = set(self.cleaned_data.get(field))
                    print("---field_val---", set_val)
                    print("---field_val_from_front", set_val_from_front)
                    if set_val!=set_val_from_front:
                        error_list.append(ValidationError(
                            _('Readonly field:%(value)s'),
                            code='invalid',
                            params={'value': field},
                        ))
                        self.add_error("tags","readonly field")
                    continue
                field_val_from_front = self.cleaned_data.get(field)
                if field_val != field_val_from_front:
                    error_list.append(ValidationError(
                        _('Readonly field:%(value)s,date should be %(val)s'),
                        code='invalid',
                        params={'value':field,'val':field_val},
                    ))

        #判断table_readonly
        if admin_class.table_readonly:
            raise ValidationError(
                _('table is readonly ,connot submit'),
                code='invalid',
                params={},
            )
        self.ValidationError = ValidationError
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)
        if error_list:
            raise ValidationError(error_list)



    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields

    attrs = {'Meta':Meta}
    _model_form_class = type("DynamicModelForm",(ModelForm,),attrs)
    setattr(_model_form_class,'__new__',__new__)
    setattr(_model_form_class,'clean',default_clean)
    return _model_form_class