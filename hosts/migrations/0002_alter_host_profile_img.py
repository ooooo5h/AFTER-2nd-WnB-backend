# Generated by Django 4.0.6 on 2022-10-20 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hosts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='profile_img',
            field=models.CharField(max_length=200, null=True),
        ),
    ]