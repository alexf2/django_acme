# Generated by Django 3.2.16 on 2024-01-22 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('birthday', '0007_auto_20240122_2110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'таг', 'verbose_name_plural': 'Таги'},
        ),
    ]