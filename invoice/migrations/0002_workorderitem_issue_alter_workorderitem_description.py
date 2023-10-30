# Generated by Django 4.2.6 on 2023-10-27 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorderitem',
            name='issue',
            field=models.TextField(blank=True, max_length=125, null=True),
        ),
        migrations.AlterField(
            model_name='workorderitem',
            name='description',
            field=models.TextField(blank=True, max_length=35, null=True),
        ),
    ]
