# Generated by Django 5.0.2 on 2025-05-11 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0007_userprofile_agreement_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='card_number',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='شماره کارت'),
        ),
    ]
