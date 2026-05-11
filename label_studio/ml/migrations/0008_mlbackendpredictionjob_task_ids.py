from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0007_auto_20240314_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlbackendpredictionjob',
            name='task_ids',
            field=models.JSONField(
                help_text='Ordered list of task IDs submitted in this prediction job',
                null=True,
                verbose_name='task ids',
            ),
        ),
    ]
