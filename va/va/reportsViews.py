from django.shortcuts import render_to_response
import random, time, redis, pickle, string, datetime
from __builtin__ import str
from genericutils import *
from reportsutils import *
from va.models import *
from forms import *
from django.conf import settings  # import the settings file
from django.template.response import TemplateResponse
from django.template import *


def basic_info(request):   
    data = initialize_data(request)
    form_details = get_search_form(request)
    cached_site_data = check_data_availability(request) 
     
   
    current_site = getCurrentSiteName(request.user.id,  request.GET.get('siteID')).upper()
    subtitle = "<i style='font-weight:200'>causes and age of death</i>"
    date_filter = ""
    if (request.GET.get('startDate') and request.GET.get('startDate') != None and request.GET.get('endDate') and request.GET.get('endDate') != None):
        date_filter += format_date(request.GET.get('startDate')) + " to " + format_date(request.GET.get('endDate'))
    elif(request.GET.get('startDate') and request.GET.get('startDate') != None):
        date_filter += "from " +  format_date(request.GET.get('startDate')) + " onwards"
    elif(request.GET.get('endDate') and request.GET.get('endDate') != None):
        date_filter += "until " +  format_date(request.GET.get('endDate')) + "</small>"
    else:
        date_filter = "All Data"
        
    subtitle = subtitle.title()
  
    
    date_filter = '<h4 class="date_filter">Time Period: <span>' + date_filter + '</span></h4>'
    last_update = '<h5 class="last_updated">Data updated as of: <span>' + get_site_last_upload(request.user.id,  request.GET.get('siteID')) + '<span></h5>'
    title = '<h3 >' + current_site + " - " + subtitle  + '</h3>'+date_filter+last_update
    
    if(cached_site_data):
        cause_of_death_all_locations_data = get_reports_data(cached_site_data, form_details, "cause_of_death_all_locations") 
        death_by_agegroup_and_cause = get_reports_data(cached_site_data, form_details, "death_by_agegroup_and_cause")
        death_by_month = get_reports_data(cached_site_data, form_details, "death_by_month")
        age_at_death = get_reports_data(cached_site_data, form_details, "age_at_death")
        cause_of_death_by_location = get_reports_data(cached_site_data, form_details, "cause_of_death_by_location")
        
        data.update({
                     'cause_of_death_all_locations': json.dumps(cause_of_death_all_locations_data), 
                     "death_by_agegroup_and_cause": json.dumps(death_by_agegroup_and_cause),  
                     "death_by_month": json.dumps(death_by_month),
                     "age_at_death": json.dumps(age_at_death),
                     "cause_of_death_by_location": json.dumps(cause_of_death_by_location),
                     "title": title
                     })
        
        return render_to_response('charts/basic_info.html', data, context_instance=RequestContext(request))
    else:
        stack_display = "Data could not be read off pickles/redis"
        error_string = "Sorry, there is no data available to display the reports. Please contact admin."
        data.update({'error': error_string, 'stack_display': stack_display, 'title': 'charts'})
        
        return render_to_response('charts/error.html', data, context_instance=RequestContext(request))
        


   
def care_issues(request):     
    data = initialize_data(request)
    form_details = get_search_form(request)
    cached_site_data = check_data_availability(request)  
    
    current_site = getCurrentSiteName(request.user.id,  request.GET.get('siteID')).upper()
    subtitle = "<i style='font-weight:200'>issues in acessing care</i>"
    date_filter = ""
    if (request.GET.get('startDate') and request.GET.get('startDate') != None and request.GET.get('endDate') and request.GET.get('endDate') != None):
        date_filter += format_date(request.GET.get('startDate')) + " to " + format_date(request.GET.get('endDate'))
    elif(request.GET.get('startDate') and request.GET.get('startDate') != None):
        date_filter += "from " +  format_date(request.GET.get('startDate')) + " onwards"
    elif(request.GET.get('endDate') and request.GET.get('endDate') != None):
        date_filter += "until " +  format_date(request.GET.get('endDate')) + "</small>"
    else:
        date_filter = "All Data"
        
    subtitle = subtitle.title()
  
    
    date_filter = '<h4 class="date_filter">Time Period: <span>' + date_filter + '</span></h4>'
    last_update = '<h5 class="last_updated">Data updated as of: <span>' + get_site_last_upload(request.user.id,  request.GET.get('siteID')) + '<span></h5>'
    title = '<h3 >' + current_site + " - " + subtitle  + '</h3>'+date_filter+last_update
    
    if(cached_site_data):
        deaths_by_duration_of_illness = get_reports_data(cached_site_data, form_details, "deaths_by_duration_of_illness")
        deaths_by_distance_to_hf = get_reports_data(cached_site_data, form_details, "deaths_by_distance_to_hf")
        deaths_by_social_reason_and_cause = get_reports_data(cached_site_data, form_details, "deaths_by_social_reason_and_cause")
        deaths_by_social_reason_and_village =  get_reports_data(cached_site_data, form_details, "deaths_by_social_reason_and_village")
        deaths_by_prob_accessing_care = get_reports_data(cached_site_data, form_details, "deaths_by_prob_accessing_care")
        
        data.update({
                      'deaths_by_duration_of_illness': json.dumps(deaths_by_duration_of_illness),
                      'deaths_by_distance_to_hf': json.dumps(deaths_by_distance_to_hf),
                      'deaths_by_social_reason_and_cause': json.dumps(deaths_by_social_reason_and_cause),
                      'deaths_by_social_reason_and_village': json.dumps(deaths_by_social_reason_and_village),
                      'deaths_by_prob_accessing_care': json.dumps(deaths_by_prob_accessing_care),
                      'title': title
                      })
        
        return render_to_response('charts/care_issues.html', data, context_instance=RequestContext(request))
    
    else :
        stack_display = "Data could not be read off pickles/redis"
        error_string = "Sorry, there is no data available to display the reports. Please contact admin."
        data.update({'error': error_string, 'stack_display': stack_display, 'title': 'charts'})
        return render_to_response('charts/error.html', data, context_instance=RequestContext(request))

 

def care_specifications(request):
    data = initialize_data(request)
    form_details = get_search_form(request)
    cached_site_data = check_data_availability(request)  
    
    current_site = getCurrentSiteName(request.user.id,  request.GET.get('siteID')).upper()
    subtitle = "<i style='font-weight:200'>care specifications</i>"
    date_filter = ""
    if (request.GET.get('startDate') and request.GET.get('startDate') != None and request.GET.get('endDate') and request.GET.get('endDate') != None):
        date_filter += format_date(request.GET.get('startDate')) + " to " + format_date(request.GET.get('endDate'))
    elif(request.GET.get('startDate') and request.GET.get('startDate') != None):
        date_filter += "from " +  format_date(request.GET.get('startDate')) + " onwards"
    elif(request.GET.get('endDate') and request.GET.get('endDate') != None):
        date_filter += "until " +  format_date(request.GET.get('endDate')) + "</small>"
    else:
        date_filter = "All Data"
        
    subtitle = subtitle.title()
  
    
    date_filter = '<h4 class="date_filter">Time Period: <span>' + date_filter + '</span></h4>'
    last_update = '<h5 class="last_updated">Data updated as of: <span>' + get_site_last_upload(request.user.id,  request.GET.get('siteID')) + '<span></h5>'
    title = '<h3 >' + current_site + " - " + subtitle  + '</h3>'+date_filter+last_update
    if(cached_site_data):
        facility_where_care_received = get_reports_data(cached_site_data, form_details, "facility_where_care_received")
        cases_treated_at_facility = get_reports_data(cached_site_data, form_details, "cases_treated_at_facility")
        cases_treated_by_chw = get_reports_data(cached_site_data, form_details, "cases_treated_by_chw")
        data.update({
                      'facility_where_care_received': facility_where_care_received,
                      'cases_treated_at_facility': cases_treated_at_facility,
                      'cases_treated_by_chw': cases_treated_by_chw,
                      'title': title
                      })
        return render_to_response('charts/care_specifications.html', data, context_instance=RequestContext(request))
    else:
        stack_display = "Data could not be read off pickles/redis"
        error_string = "Sorry, there is no data available to display the reports. Please contact admin."
        data.update({'error': error_string, 'stack_display': stack_display, 'title': 'charts'})
        return render_to_response('charts/error.html', data, context_instance=RequestContext(request))

        
        
    

