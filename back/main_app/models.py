from django.db import models
from django.utils import timezone


class Frame(models.Model):
    fullness = models.FloatField('Fullness')
    timestamp = models.DateTimeField('Timestamp', default=timezone.now)


class Rock(models.Model):
    frame = models.ForeignKey('Frame', on_delete=models.CASCADE, verbose_name='Frame',
                              related_name='rock', null=True)
    max_size = models.IntegerField('Max size')
