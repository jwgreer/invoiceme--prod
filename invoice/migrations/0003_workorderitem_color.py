# Generated by Django 4.2.5 on 2023-11-13 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0002_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='workorderitem',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='invoice.color'),
        ),
    ]
