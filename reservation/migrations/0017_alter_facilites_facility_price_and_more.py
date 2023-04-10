# Generated by Django 4.1.7 on 2023-04-09 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservation", "0016_billing_reference_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="facilites",
            name="facility_price",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="services",
            name="service_price",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
