# Generated by Django 4.1.7 on 2023-04-10 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservation", "0018_reserveconsulation_patient_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reserveconsulation",
            name="schedule",
            field=models.DateTimeField(editable=False),
        ),
    ]
