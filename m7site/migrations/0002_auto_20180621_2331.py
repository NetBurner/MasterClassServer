# Generated by Django 2.0.6 on 2018-06-21 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m7site', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='uuid',
            field=models.CharField(max_length=50),
        ),
    ]
