# Generated by Django 2.0.6 on 2018-06-28 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('m7site', '0002_auto_20180621_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='switch',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
