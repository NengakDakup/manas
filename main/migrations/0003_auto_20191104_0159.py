# Generated by Django 2.2.6 on 2019-11-04 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_notifications_predictionhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('prediction', models.CharField(choices=[('N', 'drought'), ('A', 'almost_drought'), ('F', 'normal')], max_length=1)),
                ('date_predicted', models.DateTimeField()),
                ('uid', models.UUIDField(editable=False)),
            ],
        ),
        migrations.DeleteModel(
            name='PredictionHistory',
        ),
    ]
