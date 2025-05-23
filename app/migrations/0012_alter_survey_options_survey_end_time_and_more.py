# Generated by Django 5.1.3 on 2024-12-02 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_remove_surveyresponse_gender'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['-created_at'], 'verbose_name': '问卷', 'verbose_name_plural': '问卷'},
        ),
        migrations.AddField(
            model_name='survey',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='结束时间'),
        ),
        migrations.AddField(
            model_name='survey',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='是否为默认问卷'),
        ),
        migrations.AddField(
            model_name='survey',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='开始时间'),
        ),
    ]
