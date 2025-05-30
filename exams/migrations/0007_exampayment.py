# Generated by Django 5.0.2 on 2025-05-12 12:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0006_alter_sitesettings_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='مبلغ پرداختی (تومان)')),
                ('payment_date', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ پرداخت')),
                ('payment_image', models.ImageField(blank=True, null=True, upload_to='exams/payments/', verbose_name='تصویر پرداخت')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.exam', verbose_name='آزمون')),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exams.examregistration', verbose_name='ثبت\u200cنام')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'پرداخت آزمون',
                'verbose_name_plural': 'پرداخت\u200cهای آزمون',
                'ordering': ['-payment_date'],
            },
        ),
    ]
