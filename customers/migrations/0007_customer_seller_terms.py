from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0006_customer_type_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='price_negotiability',
            field=models.CharField(
                blank=True,
                choices=[('NEGOTIABLE', 'Negotiable'), ('FIXED', 'Not negotiable')],
                max_length=12,
            ),
        ),
        migrations.AddField(
            model_name='customer',
            name='title_type',
            field=models.CharField(
                blank=True,
                choices=[('HARD', 'Hard Title'), ('SOFT', 'Soft Title')],
                max_length=10,
            ),
        ),
    ]
