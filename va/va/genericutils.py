import arrow
from datetime import datetime as thedatetime, timedelta, date
import datetime
from dateutil import relativedelta
from django.http import Http404
from __builtin__ import str
from models import *


def format_date(datestr):
    datestr = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    return datestr.strftime('%m/%d/%Y')
def getCurrentUser(userid):
    try:
        user = Users.objects.get(authid_id=userid)
    except:
        user = None
    return user

def getCurrentSiteName(userid, site_id):
    try:
        if(site_id):
            site = Sites.objects.get(siteid=site_id)
            return site.name
        elif(userid):
            user = getCurrentUser(userid)
            if(user):
                site = Sites.objects.get(siteid=user.siteid_id)
                return site.name
            
    except Exception, e:
        site = ""
        return site

def get_site_last_upload(userid, site_id):
    try:
        if(site_id):
            site = Sites.objects.get(siteid=site_id)
        elif(userid):
            user = getCurrentUser(userid)
            if(user):
                site = Sites.objects.get(siteid=user.siteid_id)
        
        if(site):
            upload = RawDataFiles.objects.get(fileid=site.current_fileid)
            if(upload):
                dateobj = upload.datecached 
        
                return str(dateobj.strftime("%m/%d/%Y %I:%M:%S %p"))
            
    except Exception, e:
        site = ""
        return str(e)

def getCurrentSiteDataKey(userid, site_id):
    try:
        if(site_id):
            site = Sites.objects.get(siteid=site_id)
            return site.datakey
        elif(userid):
            user = getCurrentUser(userid)
            if(user):
                site = Sites.objects.get(siteid=user.siteid_id)
                return site.datakey
            
    except Exception, e:
        key = ""
        return key

def cleanString(myString):
    return myString.lower().strip().title()

def withinRange(startDate, endDate, vaDate):
    if(not startDate and not endDate):
        return True
    elif(startDate and endDate):
        if(vaDate >= startDate and vaDate <= endDate):
            return True
    elif(startDate and not endDate):
       if(vaDate >= startDate):
            return True
    elif(endDate and not startDate):
       if(vaDate <= endDate):
            return True
        
        
def get_age_groups():
    groups  = {
               "still": "Stillbirth",
               "0-1": "0-1 days",
               "2-3": "2-3 days",
               "4-7": "4-7 days",
               "8-14": "8-14 days",
               "15-21": "15-21 days",
               "22-28": "22-28 days",
               "29-365": "29-365 days",
               "366-1825": "366-1825 days",
               "other": "Other"
               }
    
    return groups


def get_age_groups_list():
    groups  = [
               "Stillbirth",
               "0-1 days",
                "2-3 days",
                "4-7 days",
               "8-14 days",
               "15-21 days",
               "22-28 days",
               "29-365 days",
                "366-1825 days",
               "maternity"
               ]
    _groups = []
    
    for group in groups:
        _groups.append(group.title())
    
    return _groups

def get_months_list(startDate, endDate):
    try:
         if(not startDate and not endDate):
           endDate = date.today()
           a = relativedelta.relativedelta(months = -12)
           
           startDate = endDate + a
           
         elif(startDate and not endDate):
            a = relativedelta.relativedelta(months = 12)
            endDate = startDate + a
            
         elif(endDate and not startDate):
            a = relativedelta.relativedelta(months = -12)
            startDate = endDate + a
         
         m_list = []
         startDate =datetime.datetime(startDate.year, startDate.month, startDate.day) #thedatetime(startDate, '%Y-%m-%d')   #datetime.datetime(2013, 2, 5)
         endDate = datetime.datetime(endDate.year, endDate.month, endDate.day)
         for d in arrow.Arrow.range('month', startDate, endDate):
            m_list.append(str(d.format('MMM-YYYY')))
         
         return m_list
    except Exception, err:
        raise Http404(str(err) + str(endDate))
    


def get_months_object_list(startDate, endDate):
    try:
         if(not startDate and not endDate):
           endDate = date.today()
           a = relativedelta.relativedelta(months = -12)
           
           startDate = endDate + a
           
         elif(startDate and not endDate):
            a = relativedelta.relativedelta(months = 12)
            endDate = startDate + a
            
         elif(endDate and not startDate):
            a = relativedelta.relativedelta(months = -12)
            startDate = endDate + a
         
         m_list = []
         startDate =datetime.datetime(startDate.year, startDate.month, startDate.day) #thedatetime(startDate, '%Y-%m-%d')   #datetime.datetime(2013, 2, 5)
         endDate = datetime.datetime(endDate.year, endDate.month, endDate.day)
         for d in arrow.Arrow.range('month', startDate, endDate):
            m_list.append([d.format('MMMM'), d.format('YYYY')])
        
         return m_list
    except Exception, err:
        raise Http404(str(err) + str(endDate))
    

def is_chart_candidate(group, age):
    if(group == "Stillbirth"):
        return True
    elif(group == "0-1 days"):
        return True
    elif(group == "2-3 days" ):
        return True
    elif(group == "4-7 days"):
        return True
    elif(group == "8-14 days"):
        return True
    elif(group == "15-21 days"):
        return True
    elif(group == "22-28 days"):
        return True
    elif(group == "29-365 days"):
        return True
    elif(group == "366-1825 days"):
        return True
                     
                     
def get_duration_of_illness_list():
    durations =  [
            "stillbirth", 
            "<24 hours", 
            ">24 hours",
            "2-7 days", 
            "8-30 days",
            ">30 days",
            "no information"
            ]    
    _durations = []
    
    for duration in durations:
        _durations.append(duration.title())
    
    return _durations   


def get_distance_from_hf_list():
    distances =  [ 
            "0-2 km", 
            "2-10 km", 
            "10+ km"
            ]   
    
    _distances = []
    
    for distance in distances:
        _distances.append(distance.title())
    
    return _distances   
   
     
        

        
        
