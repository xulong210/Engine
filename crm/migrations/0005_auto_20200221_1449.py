# Generated by Django 2.2.5 on 2020-02-21 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_userprofile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='邮箱'),
        ),
        migrations.AddField(
            model_name='customer',
            name='nums_id',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='身份证号'),
        ),
    ]
