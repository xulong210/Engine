#__author:"xulong"
#date:   2020/2/20
from django.utils.translation import ugettext as _
from django.forms import ModelForm,ValidationError
from crm import models


class EnrollmentForm(ModelForm):
    def __new__(cls,*args,**kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)
    class Meta:
        model = models.Enrollment
        fields = ["enrolled_class","consultant"]

class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'
        return ModelForm.__new__(cls)

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ['tags','content','memo','status','consult_course','referral_from']
        readonly_fields = ['qq','consultant','source']

    def clean(self):
        error_list = []
        for field in self.Meta.readonly_fields:
            field_val = getattr(self.instance,field)
            if hasattr(field_val,"select_related"):
                field_val = getattr(field_val,"select_related")
                queryset = field_val.select_related()
                set_val = set(queryset)
                set_val_from_front = set(self.cleaned_data.get(field))
                if set_val != set_val_from_front:
                    error_list.append(ValidationError(
                        _("the field %(value)s ,the value %(val)s ,cannot be changed"),
                        code="invalid",
                        params={"value": field, "val": set_val},
                    ))
                continue
            field_val_from_front = self.cleaned_data.get(field)
            if field_val != field_val_from_front:
                error_list.append(ValidationError(
                    _("the field %(value)s ,the value %(val)s ,cannot be changed"),
                    code="invalid",
                    params={"value":field,"val":field_val},
                ))
        if error_list:
            raise ValidationError(error_list)