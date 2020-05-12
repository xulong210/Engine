#__author:"xulong"
#date:   2020/1/24
from django.db.models import Q

def table_filter(request,admin_class):
    '''进行条件过滤并返回过滤后的数据'''

    filter_conditions = {}
    for k,v in request.GET.items():
        '''
        {'source':1,'consultant':1,'page':1} 分页关键字不可以作为数据库索引字段 须去除
        '''
        keywords = ['page','o','_q']
        if k in keywords: #保留的分页关键字 / 和排序关键字
            continue
        if v:
            filter_conditions[k] = v
            # k是指过滤的指标 如 source 按source来分
            # v 是 数据
            #例如 source:转介绍
    return admin_class.model.objects.filter(**filter_conditions),filter_conditions
'''
第一次进入页面因为过滤器没有发送GET请求 所以filter_conditions为空 
即admin_class.model.objects.filter() 返回所有数据
'''


def table_sort(request,admin_class,objects):
    orderby_key = request.GET.get('o')
    if orderby_key:
        res = objects.order_by(orderby_key)
        if orderby_key.startswith("-"):
            orderby_key = orderby_key.strip("-")
        else:
            orderby_key = "-%s" % orderby_key
    else:
        res = objects
    return res,orderby_key


def table_search(request,admin_class,object_list):
    search_key = request.GET.get("_q","")
    if search_key:
        q_obj = Q()
        q_obj.connector = "OR"
        for column in admin_class.search_fields:
            q_obj.children.append(("%s__contains"%column,search_key))
        res = object_list.filter(q_obj)
    else:
        res = object_list
    return res
