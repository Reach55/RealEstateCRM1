from django.db import migrations, models


def normalize_customer_types(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    database = schema_editor.connection.alias
    Customer.objects.using(database).filter(customer_type='TENANT').update(customer_type='RENTER')
    Customer.objects.using(database).filter(customer_type='OWNER_SELL').update(customer_type='SELLER')
    Customer.objects.using(database).filter(customer_type='OWNER_RENT').update(customer_type='RENT_OWNER')


def restore_previous_customer_types(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    database = schema_editor.connection.alias
    Customer.objects.using(database).filter(customer_type='RENTER').update(customer_type='TENANT')
    Customer.objects.using(database).filter(customer_type='RENT_OWNER').update(customer_type='OWNER_RENT')


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_alter_customer_customer_type'),
    ]

    operations = [
        migrations.RunPython(normalize_customer_types, restore_previous_customer_types),
        migrations.AlterField(
            model_name='customer',
            name='customer_type',
            field=models.CharField(
                choices=[
                    ('BUYER', 'Buyer'),
                    ('SELLER', 'Seller'),
                    ('RENTER', 'Renter'),
                    ('RENT_OWNER', 'Property Rent Owner'),
                ],
                default='BUYER',
                max_length=20,
            ),
        ),
    ]
