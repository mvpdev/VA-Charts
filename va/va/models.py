# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Sites(models.Model):
    """
    All the Millenium villages for which VA reports should be generated
    """
    STATUS_ACTIVE = 1
    STATUS_INACTIVE = 2

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"))
    siteid = models.AutoField(primary_key=True, verbose_name="Site")
    domain = models.CharField(unique=True, max_length=255)
    name = models.CharField(unique=True, max_length=255)
    datakey = models.CharField(unique=True, max_length=255)
    status = models.SmallIntegerField(choices=STATUS_CHOICES)
    current_fileid = models.IntegerField(null=True)
    datecreated = models.DateTimeField(auto_now=True)
    datemodified = models.DateTimeField(auto_now=True, auto_now_add=True)
    
    def __unicode__(self):
        return self.name




class Users(models.Model):

    ADMIN = 1
    NORMAL = 2
    USER_TYPES_CHOICES = (
                          (ADMIN, 'Admin'),
                          (NORMAL, 'Normal User')
                          )

    userid = models.AutoField(primary_key=True, verbose_name="user", db_index=True)
    authid = models.ForeignKey(User, blank=True, null=True)
    siteid = models.ForeignKey(Sites, blank=True, null=True, verbose_name="Site")
    firstname = models.CharField(max_length=255, verbose_name="First Name")
    lastname = models.CharField(max_length=255, verbose_name="Last Name")
    emailaddress = models.EmailField(max_length=150, verbose_name="Email Address")
    status = models.IntegerField(default=1)
    datecreated = models.DateTimeField(auto_now=True)
    datemodified = models.DateTimeField(auto_now=True, auto_now_add=True)
    lastloginip = models.IPAddressField(null=True)
    lastlogindate = models.DateTimeField(null=True)
    usertype = models.PositiveIntegerField(choices=USER_TYPES_CHOICES, verbose_name="Please select type of user")

    def __unicode__(self):
        return self.firstname.upper()+" "+self.lastname.upper()



class RawDataFiles(models.Model):
    """
    Stores the VA forms excel file downloads for various sites
    """
    
    STATUS_ACTIVE = 1
    STATUS_INACTIVE = 2

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"))
    fileid = models.AutoField(primary_key=True)
    siteid = models.ForeignKey('Sites', verbose_name="Site")
    filename = models.FileField(max_length=100, upload_to="data/va/uploads", verbose_name="Upload File")
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default="2", verbose_name="Status")
    narration = models.TextField(blank=True, null=True, verbose_name="Narration")
    uploadedby =  models.ForeignKey(Users, blank=True, null=True)
    datecreated = models.DateTimeField(auto_now=True)
    datemodified = models.DateTimeField(auto_now=True, auto_now_add=True)
    datecached = models.DateTimeField(null=True)
    refreshcache = models.BooleanField(default=False)
    




