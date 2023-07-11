# Generated by Django 4.1.7 on 2023-07-11 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservation", "0010_alter_reserveconsulation_timeslot"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reserveconsulation",
            name="timeslot",
            field=models.CharField(
                choices=[
                    ("1", "8-9AM"),
                    ("2", "10-11AM"),
                    ("3", "12-1PM"),
                    ("4", "2-3PM"),
                    ("5", "4-5PM"),
                ],
                max_length=1,
                null=True,
            ),
        ),
    ]
