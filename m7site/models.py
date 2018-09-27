from django.db import models

class Command(models.Model):
    class_name = models.CharField(max_length=255, null=False)
    name = models.CharField(max_length=255, null=False)

class Client(models.Model):
    uuid = models.CharField(max_length=50, null=False, unique=True)
    student_name = models.CharField(max_length=255, null=False)
    current_command = models.ForeignKey(Command, on_delete=models.SET_NULL, null=True)
    response_message = models.CharField(max_length=255, null=False, default='')
    last_seen = models.DateTimeField()
    last_message = models.CharField(max_length=255, null=False, default='')
    last_switch = models.IntegerField(null=False, default=0)

class Record(models.Model):
    uuid = models.CharField(max_length=50, null=False)
    message = models.CharField(max_length=255, null=False)
    uptime = models.IntegerField(null=False)
    switch = models.IntegerField(null=False)
    created_at = models.DateTimeField(null=False)
