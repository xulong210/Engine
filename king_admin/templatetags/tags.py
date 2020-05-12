#__author:"xulong"
#date:   2020/1/19

from django import template
from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime,timedelta

register = template.Library()

'''
显示中文表名
'''
@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

'''
获取一张表中所有数据对象 .all()
'''
@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

'''
标题栏数据
'''
@register.simple_tag
def build_table_header_column(column,orderby_key,admin_class,filter_conditions):
    filter = ''
    for k, v in filter_conditions.items():
        filter += '&%s=%s' % (k, v)
    ele = '''<th><a href="?o={orderby_key}{filter}">{column}</a>
            {sort_icon}
            </th>'''
    sort_icon = ''
    try:
        field_obj = admin_class.model._meta.get_field(column)
        vb_name = field_obj.verbose_name
        if orderby_key and orderby_key.strip("-") == column:
            if orderby_key == column:
                sort_icon = '''<span class="glyphicon glyphicon-chevron-up"></span>'''
            else:
                sort_icon = '''<span class="glyphicon glyphicon-chevron-down"></span>'''
        else:
            orderby_key = column
            sort_icon = ''
    except FieldDoesNotExist as e:
        vb_name = column
        ele = '''<th><a href="javascript:void(0);">{column}</a></th>'''
        return mark_safe(ele.format(column=vb_name))
    return mark_safe(ele.format(orderby_key=orderby_key,filter=filter,column=vb_name,sort_icon=sort_icon))



'''
按list_display自定义添加数据字段
'''
@register.simple_tag
def build_table_row(obj,admin_class,request):
    row_ele = ""
    for index,column in enumerate(admin_class.list_display): #需要显示的字段名
        try:
            field_obj = obj._meta.get_field(column) #column是字符串 根据字符串获取字段对象
            if field_obj.choices:#choice type #判断是否是choice类型
                column_data = getattr(obj,"get_%s_display"%column)()
            else:
                column_data = getattr(obj,column)

            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime("%Y-%m-%d %H:%M:%S")

            if index == 0: #添加a标签 使它可以点进修改页面
                column_data = "<a href='{request_path}{obj_id}/change/'>{data}</a>".format(request_path=request.path,obj_id=column_data,data=column_data)
        except FieldDoesNotExist as e:
            if hasattr(admin_class,column):
                column_func = getattr(admin_class,column)
                admin_class.instance = obj
                #admin_class.request = request
                column_data = column_func()
        row_ele += "<td>%s</td>" % column_data
    return mark_safe(row_ele)

@register.simple_tag
def render_filter_ele(condition,admin_class,filter_conditions):
    select_ele = '''<select class="form-control" name="{condition}"><option value=''>---</option>'''
    field_obj = admin_class.model._meta.get_field(condition) # source
    if field_obj.choices:
        selected = ""
        for choice_item in field_obj.choices:
            if filter_conditions.get(condition) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value="%s" %s>%s</option>'''%(choice_item[0],selected,choice_item[1])
            selected = ""
    if type(field_obj).__name__ =="ForeignKey":
        selected = ""
        for choice_item in field_obj.get_choices()[1:]:
            if filter_conditions.get(condition) == str(choice_item[0]):
                selected = "selected"
            select_ele += '''<option value="%s" %s>%s</option>'''%(choice_item[0],selected,choice_item[1])
            selected = ""
    if type(field_obj).__name__ in ("DateTimeField","DateField"):
        date_els = []
        today_ele = datetime.now().date() #先获取当前日期+时间 再舍去时间 -> 2020/1/20
        date_els.append(["今天",datetime.now().date()])
        date_els.append(["昨天",today_ele - timedelta(days=1)])
        date_els.append(["近7天",today_ele - timedelta(days=7)])
        date_els.append(["本月",today_ele.replace(day=1)])
        date_els.append(["近30天",today_ele - timedelta(days=90)])
        date_els.append(["近90天",today_ele - timedelta(days=90)])
        date_els.append(["近180天",today_ele - timedelta(days=180)])
        date_els.append(["本年",today_ele.replace(month=1,day=1)])
        date_els.append(["近365天",today_ele - timedelta(days=365)])
        selected = ""

        for item in date_els:
            select_ele += '''<option value='%s' %s>%s</option>'''%(item[1],selected,item[0])

            condition_name = "%s__gte" % condition
    else:
        condition_name = condition
    select_ele += "</select>"
    select_ele = select_ele.format(condition=condition_name)
    return mark_safe(select_ele)
'''
source_obj = models.Customer._meta.get_field("source")
source_obj.choices #返回结果
((0, '转介绍'),
 (1, 'QQ群'),
 (2, '官网'),
 (3, '百度推广'),
 (4, '51CTO'),
 (5, '知乎'),
 (6, '市场推广'))'''

'''
consultant_obj = models.Customer._meta.get_field('consultant')
consultant_obj.get_choices()
Out[8]: [('', '---------'), (1, 'root xu'), (2, 'xulong')]'''
# @register.simple_tag
# def render_page_ele(loop_counter,query_sets,filter_conditions):
#     filter = ''
#     for k,v in filter_conditions.items():
#         filter += '&%s=%s'% (k,v)
#
#     if loop_counter < 3 or loop_counter > query_sets.paginator.num_pages - 2:
#         ele_class = ""
#         if query_sets.number == loop_counter:
#             ele_class = "active"
#         ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, loop_counter, filter, loop_counter)
#
#         return mark_safe(ele)
#
#     if abs(query_sets.number - loop_counter) <= 1:
#         ele_class = ""
#         if query_sets.number == loop_counter:
#             ele_class = "active"
#         ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' %(ele_class,loop_counter,filter,loop_counter)
#
#         return mark_safe(ele)
#
#     return ''

@register.simple_tag
def build_paginators(query_sets,filter_conditions,orderby_key,search_key):
    if orderby_key:
        filter = '&_q=%s&o=%s'% (search_key,orderby_key.strip("-")) if orderby_key.startswith("-") else '&o=-%s'% orderby_key
    else:
        filter = "&_q=%s" %(search_key)
    for k,v in filter_conditions.items():
        filter += '&%s=%s' % (k,v)

    page_btns = ''
    ignore_display = False
    for page_num in query_sets.paginator.page_range:
        if page_num < 3 or page_num > query_sets.paginator.num_pages - 2 \
                or abs(query_sets.number - page_num)<=1: #判断最前两页和最后两页
            ele_class = ""
            if query_sets.number == page_num:
                ignore_display = False
                ele_class = "active"
            page_btns += '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, page_num, filter, page_num)
        # elif abs(query_sets.number - page_num)<=1: #判断前后一页
        #     ele_class = ""
        #     if query_sets.number == page_num:
        #         ignore_display = False
        #         ele_class = "active"
        #     page_btns += '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, page_num, filter, page_num)
        else: #显示 ...
            if ignore_display == False: #还没有加
                page_btns += '<li><a>...</a></li>'
                ignore_display = True
    return mark_safe(page_btns)

@register.simple_tag
def build_previous_page(query_sets,filter_conditions,orderby_key,search_key):
    if orderby_key:
        filter = '&_q=%s&o=%s'% (search_key,orderby_key.strip("-")) if orderby_key.startswith("-") else '&o=-%s' % orderby_key
    else:
        filter = "&_q=%s" %(search_key)
    for k, v in filter_conditions.items():
        filter += '&%s=%s' % (k, v)
    btn = '<a href="?page=%s%s">%s</a>' % (query_sets.previous_page_number(),filter,"上页")
    return mark_safe(btn)

@register.simple_tag
def build_next_page(query_sets,filter_conditions,orderby_key,search_key):
    if orderby_key:
        filter = '&_q=%s&o=%s'% (search_key,orderby_key.strip("-")) if orderby_key.startswith("-") else '&o=-%s'% orderby_key
    else:
        filter = "&_q=%s" %(search_key)
    for k, v in filter_conditions.items():
        filter += '&%s=%s' % (k, v)
    btn = '<a href="?page=%s%s">%s</a>' % (query_sets.next_page_number(),filter,"下页")
    return mark_safe(btn)

@register.simple_tag
def render_action_name(action,admin_class):
    if hasattr(admin_class,action):
        action = getattr(admin_class,action)
    return action.display_name

@register.simple_tag
def render_field_name(column,admin_class):
    field_obj = admin_class.model._meta.get_field(column)
    return field_obj.verbose_name

@register.simple_tag
def get_m2m_obj_list(admin_class,field):
    '''返回m2m所有备选数据 制作左右移动框进行多选'''
    #表结构对象中的某个字段
    field_obj = getattr(admin_class.model,field.name)
    '''(models.Customer).tags.rel.model.objects.all()'''
    #field.name 是字段名 即tags 是字符串

    return field_obj.rel.model.objects.all()

@register.simple_tag
def get_m2m_selected_obj_list(form_obj,field):
    '''返回已选择的m2m数据'''
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance,field.name) # crm.tags
        '''form_obj.instance.tags.all==>crm.tags.all()'''
        return field_obj.all()
    else: #代表在创建新的记录
        return []




@register.simple_tag
def print_obj_methods(obj):
    print("debug {obj}".center(50,"-").format(obj=obj))
    print(dir(obj))


def recursive_related_objs_lookup(objs):
    ul_ele = "<ul>"
    for obj in objs: #obj是all()中的一条querySet数据
        li_ele = '''<li>%s : %s</li>'''%(obj._meta.verbose_name,obj.__str__())
        '''obj._meta.verbose_name返回表名'''
        '''str是自己在model中写的方法'''
        '''客户表:952412165'''
        ul_ele += li_ele

        '''记录多对多数据 即在自己表中建立的多对多关系'''
        for m2m_field in obj._meta.local_many_to_many:
            '''obj._meta.local_many_to_many 返回[<django.db.models.fields.related.ManyToManyField: tags>]'''
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name)
            '''m2m_field.name 返回字符串tags'''
            for o in m2m_field_obj.select_related():
                '''for o in obj.tags.select_related 能获取所有相关联的tag数据'''
                '''<QuerySet [<Tag: 中国>, <Tag: 法国>]>'''
                li_ele = '''<li>%s : %s</li>'''%(m2m_field.verbose_name,o.__str__())
                '''obj._meta.local_many_to_many[0].verbose_name 返回字符串tags'''
                sub_ul_ele += li_ele
            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele

        #对于一对多
        for related_obj in obj._meta.related_objects:
            '''obj._meta.related_objects 返回所有一对多/多对多关系的表，即本条数据被作为其他表的外键'''
            '''
            (<ManyToOneRel: crm.customerfollowup>,
            <ManyToOneRel: crm.enrollment>,
            <ManyToOneRel: crm.payment>)
            '''
            if 'ManyToManyRel' in related_obj.__repr__(): #repr就是返回字符串形式
                '''多对多关系 在别的表中建立的m2m'''
                # '<ManyToOneRel: crm.customerfollowup>'
                if hasattr(obj,related_obj.get_accessor_name()):
                    accessor_obj = getattr(obj,related_obj.get_accessor_name())
                    if hasattr(accessor_obj,"select_related"):
                        target_objs = accessor_obj.select_related()
                        sub_ul_ele = "<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li>%s:%s</li>'''%(o._meta.verbose_name,o.__str__())
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj,related_obj.get_accessor_name()):
                accessor_obj = getattr(obj, related_obj.get_accessor_name())
                '''
                related_obj.get_accessor_name()  :  'enrollment_set'
                obj.enrollment_set  //进行反查询
                '''
                if hasattr(accessor_obj,'select_related'):
                    # selected_related == all  反查询
                    target_objs = accessor_obj.select_related()
                    #等价于 accessor_obj.all()  ==> obj.xx_set.all() ==> obj.xx_set.select_related()
                else:
                    target_objs = []
                if len(target_objs) > 0:
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele += "</ul>"
    return ul_ele



@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关的数据取出来'''
    #objs = [objs,] #原本是修改页面删除 只有一个对象转为列表
    if objs:
        '''开始递归打印数据'''
        return mark_safe(recursive_related_objs_lookup(objs))