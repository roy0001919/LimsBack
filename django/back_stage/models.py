from django.db import models
from django.contrib.auth.models import User


class report_reserve_sample_test(models.Model):
    DateSampled = models.CharField(max_length=250, default='null', null=True)
    SampleReceiveDate = models.CharField(max_length=250, default='null', null=True)
    Name = models.CharField(max_length=250, default='null', null=True)
    Type = models.CharField(max_length=250, default='null', null=True)
    Sample_id = models.CharField(max_length=250, default='null', null=True)
    ClientName = models.CharField(max_length=250, default='null', null=True)
    ContactID = models.CharField(max_length=250, default='null', primary_key=True)
    Contact_uuid = models.CharField(max_length=250, default='null', null=True)
    Sample_uuid = models.CharField(max_length=250, default='null', null=True)
    Client_uuid = models.CharField(max_length=250, default='null', null=True)
    Age = models.CharField(max_length=250, default='null', null=True)
    Phone = models.CharField(max_length=250, default='null', null=True)
    Sex = models.CharField(max_length=250, default='null', null=True)
    birthday = models.CharField(max_length=250, default='null', null=True)
    ENName = models.CharField(max_length=250, default='null', null=True)
    remark = models.CharField(max_length=250, default='null', null=True)
    PID = models.CharField(max_length=250, default='null', null=True)
    ClientTo = models.CharField(max_length=250, default='null', null=True)

    def __str__(self):
         return self.Name


class custdata(models.Model):
    Name = models.CharField(max_length=250, default='null', null=True)
    ClientName = models.CharField(max_length=250, default='null', null=True)
    ContactID = models.CharField(max_length=250, default='null', null=True)
    Client_uuid = models.CharField(max_length=250, default='null', null=True)
    Contact_uuid = models.CharField(max_length=250, default='null', null=True)
    PID = models.CharField(max_length=250, default='null', null=True)
    Sample_uuid = models.CharField(max_length=250, default='null', null=True)
    Sample_id = models.CharField(max_length=250, default='null', null=True)

    def __str__(self):
         return self.Name
