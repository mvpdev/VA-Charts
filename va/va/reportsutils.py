from forms import *
from genericutils import *
import time, datetime, random, redis, pickle, json
from collections import Counter
from django.contrib.auth.tests.custom_user import groups
from django.shortcuts import render_to_response
from random import randint


def check_data_availability(request):
    
    r = redis.StrictRedis(host='localhost', port=6379, db=0) 
    try:
        key = getCurrentSiteDataKey(request.user.id,  request.GET.get('siteID'))
        site_data = pickle.loads(r.get(key))
        return site_data
    
    except Exception, e:
        return False
    
    
    
    

def initialize_data(request):
    data = {}   
    
    form_details = get_search_form(request)
    data.update(
               {
                'user': request.user,
                'form': form_details['form']
                }
               )
   
    return data


def get_search_form(request):
    form = SearchForm()
    dates = ""
    startDate = ""
    endDate = ""
    siteID = ""
    
    user = getCurrentUser(request.user.id)
    if(user):
        siteID = user.siteid_id
    if(request.method == "GET"):
        if(request.GET.get('siteID')):
            siteID =  request.GET.get('siteID')
        if(request.GET.get('startDate')):
            startDate = datetime.datetime.strptime(request.GET.get('startDate'), "%Y-%m-%d")
            form.startDate = startDate
        if(request.GET.get('endDate')):
            endDate = datetime.datetime.strptime(request.GET.get('endDate'), "%Y-%m-%d")
    
    #raise Http404(str((siteID)))
    form = SearchForm(initial = {'siteID': siteID, 'startDate': startDate, 'endDate': endDate})
    return {'form': form, 'startDate': startDate, 'endDate': endDate, 'siteID': "siteID"}



def get_reports_data(site_data, form_details, datakey):
    
    startDate = form_details['startDate']
    endDate = form_details['endDate']
    causes_container = []
    age_in_days_container = []
    death_date_and_age_container = []
    unique_causes = []
    unique_locations = []
    unique_form_types = []
    location_container = []
    location_cause_container = []
    cause_and_duration_container = []
    distance_and_formtype_container = []
    problems_and_cause_container = []
    unique_social = []
    social_and_village_container = []
    social_and_cause_container = []
    facility_care_container = []
    facility_care_cause_container = []
    case_treated_by_chw_container = []
    unique_villages = []
    unique_problems = ["Yes", "No"]
    unique_facilities = []
    unique_treated = ["Yes", "No"]
    unique_cases_treated_by_chw = ["Yes", "No"]
    
    for row in site_data:
        death_month = row[1]
        death_year = int(float(row[2]))
        age_in_days = cleanString(row[3])
        
        village = cleanString(row[4])
        mycause = cleanString(row[5])
        location = cleanString(row[6])
        form_type = cleanString(row[7])
        distance = cleanString(row[8])
        social_reason = cleanString(row[9])
        facility_question = cleanString(row[10])
        facility = cleanString(row[11])
        illness_duration = cleanString(row[12])
        prob_question = cleanString(row[13])
        case_treated_by_chw =  cleanString(row[15])
       
        
        
        vaDate = datetime.datetime.strptime('01/' + death_month + '/' + str(death_year), "%d/%B/%Y")
        if(withinRange(startDate, endDate, vaDate)):  # if within date range
            death_date_and_age_container.append([age_in_days, death_month, death_year])
            if(mycause):  # for cause of death - all locations report
                causes_container.append(mycause)
                age_in_days_container.append([age_in_days, mycause])
                if (mycause not in unique_causes):
                    unique_causes.append(mycause)
            # locations
            
            if(location):  # for cause of death by location report
                location_container.append(location)
                location_cause_container.append([location, mycause])
                if (location not in unique_locations):
                    unique_locations.append(location)
            if(illness_duration):
                cause_and_duration_container.append([mycause, illness_duration])
            if(form_type):
                distance_and_formtype_container.append([form_type, distance])
                if(form_type not in unique_form_types):
                    unique_form_types.append(form_type)
                    
            if(social_reason):
                social_and_village_container.append([social_reason, village])
                social_and_cause_container.append([social_reason, mycause])
                if(social_reason not in unique_social):
                    unique_social.append(social_reason)
                
            if(village not in unique_villages):
                unique_villages.append(village)
        
            if(prob_question):
                problems_and_cause_container.append([mycause, prob_question])
                if(prob_question not in unique_problems):
                    unique_problems.append(prob_question)
            
            
            if(facility_question):
                facility_care_cause_container.append([facility_question, facility, mycause])
                if(facility_question not in unique_treated):
                    unique_treated.append(facility_question)
                if(facility_question == "yes".title()):
                    facility_care_container.append([facility_question, facility])
                    if(facility not in unique_facilities):
                        unique_facilities.append(facility)
                        
            if(case_treated_by_chw):
                case_treated_by_chw_container.append([case_treated_by_chw, mycause])
                if(case_treated_by_chw not in unique_cases_treated_by_chw):
                    unique_cases_treated_by_chw.append(case_treated_by_chw)
                    
                    
    if(datakey == "cause_of_death_all_locations"):  # piechart
        data = get_cause_of_death_all_locations_data(causes_container, unique_causes)
        results = get_cause_of_death_all_locations_results(data)
        return results
    
    elif(datakey == "death_by_agegroup_and_cause"):  # stacked bar chart
        data = get_death_by_agegroup_and_cause_data(age_in_days_container, unique_causes)
        results = get_death_by_agegroup_and_cause_results(data)
        return results
    
    elif(datakey == "death_by_month"):  # stacked barchart
        data = get_death_by_month_data(startDate, endDate, death_date_and_age_container)
        results = get_death_by_month_results(data, startDate, endDate)
        return results
    
    elif(datakey == "age_at_death"):  # piechart
        data = get_age_at_death_data(age_in_days_container)
        results = get_age_at_death_results(data)
        return results
    
    elif(datakey == "cause_of_death_by_location"):  # stacked bar chart
        data = get_cause_of_death_by_location_data(location_cause_container, unique_causes, unique_locations)
        results = get_cause_of_death_by_location_results(data, unique_locations)
        return results
    
    elif(datakey == "deaths_by_duration_of_illness"):  # stacked barchart
        data = get_deaths_by_duration_of_illness_data(cause_and_duration_container, unique_causes)
        results = get_deaths_by_duration_of_illness_results(data)
        return results
    
    elif(datakey == "deaths_by_distance_to_hf"):  # stacked barchat
        data = get_deaths_by_distance_to_hf_data(distance_and_formtype_container, unique_form_types)
        results = get_deaths_by_distance_to_hf_results(data)
        return results
    
    elif(datakey == "deaths_by_social_reason_and_cause"):
        data = get_deaths_by_social_reason_and_cause_data(social_and_cause_container, unique_causes, unique_social)
        results = get_deaths_by_social_reason_and_cause_results(data, unique_social)
        return results
    
    elif(datakey == "deaths_by_social_reason_and_village"):
        data = get_deaths_by_social_reason_and_village_data(social_and_village_container, unique_villages, unique_social)
        results = get_deaths_by_social_reason_and_village_results(data, unique_social)
        return results
    elif(datakey == "deaths_by_prob_accessing_care"):
        data = get_deaths_by_prob_accessing_care_data(problems_and_cause_container, unique_causes, unique_problems)
        results = get_deaths_by_prob_accessing_care_results(data, unique_problems)
        return results
    
    
    #page three charts
    elif(datakey == "facility_where_care_received"): #piechart
        #return facility_care_container
        data = get_facility_where_care_received_data(unique_facilities, facility_care_container)
        results = get_facility_where_care_received_results(data)
        return results
    elif(datakey == "cases_treated_at_facility"): #stacked bar graph
        #unique_treated.sort(reverse=True)
        data = get_cases_treated_at_facility_data(facility_care_cause_container, unique_causes, unique_treated)
        results = get_cases_treated_at_facility_results(data, unique_treated)
        return results
    elif(datakey == "cases_treated_by_chw"): #stacked bargraph
        #unique_cases_treated_by_chw.sort(reverse=True)
        data = get_cases_treated_by_chw_data(case_treated_by_chw_container, unique_causes, unique_cases_treated_by_chw)
        results = get_cases_treated_by_chw_results(data, unique_cases_treated_by_chw)
        return results
        
        
    
        
    

def get_cause_of_death_all_locations_data(causes_container, unique_causes):
    counts = Counter(causes_container)
    values = []
    cause_labels = []
    for count in counts:
        values.append(counts[count])
        for cause in unique_causes:
            if cause == count:
                cause_labels.append(cause.title())
                
                
    data = []
    try:
        max_value = max(values)
        max_index = values.index(max_value)
    except:
        max_value = 0
        max_index = 0
        
    for i in range(len(values)):
        if(max_index == i):
             elem = {
                        "name": cause_labels[i],
                        "y": values[i],
                        "sliced": "true",
                        "selected": "true"
                    }
        else:
            elem = [cause_labels[i], values[i] if values[i] > 0 else None ]
        data.append(elem)
    # return [ ['Safari',    8.5]]
    return data
 

def get_cause_of_death_all_locations_results(data):
    return {
        "chart": {
             "width":600,
             "height":600,
             "type": 'pie',
                "options3d": {
                    "enabled": "true",
                    "alpha": 45,
                    "beta": 0
                }
        },
        "title": {
            "text": 'Proportion of Cause of Deaths - All Locations'.title()
        },
        
        "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '{series.name}: <b>{point.y}</b><br/>Porportion: <b>{point.percentage:.1f}%</b></a>',
        },
        "plotOptions": {
            "pie": {
                "allowPointSelect": "true",
                "cursor": 'pointer',
                "depth": 30,
                "dataLabels": {
                    "enabled": "true",
                     "format": '<b>{point.name}</b>',
                },
                "showInLegend": "true"
            }
        },
        "series": [{
            "type": 'pie',
            "name": 'Death Count',
            "data":data,
        }]
    }
    
def get_death_by_agegroup_and_cause_data(age_in_days_container, unique_causes):
    groups = get_age_groups_list()
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_cause_count_per_group_data(cause, groups, age_in_days_container),
                })
        
    return data

def get_death_by_agegroup_and_cause_results(data):
    return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Number of deaths by age group and cause' .title()
                },
                "xAxis": {
                    "categories": get_age_groups_list()
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
    

def get_cause_count_per_group_data(cause, groups, age_in_days_container):
    data = []    
    # i = 0
    stillbirth = 0
    zero_one_days = 0
    two_three_days = 0
    four_seven_days = 0
    eight_14_days = 0
    fifteen_21_days = 0
    twentytwo_28_days = 0
    twentynine_365 = 0
    threesixsix_1825 = 0
    maternity = 0
    
    for group in groups:
        for age_str in age_in_days_container:
                age = age_str[0]
                the_cause = cleanString(age_str[1])
                if(cause == the_cause):
                    if(age == group and group == "Stillbirth"):
                        stillbirth += 1
                        
                    elif(age == group  and group == "0-1 days".title()):
                        zero_one_days += 1
                            
                    elif(age == group and group == "2-3 days".title()):
                        two_three_days += 1
                            
                    elif(age == group and group == "4-7 days".title()):
                            four_seven_days += 1  
                    
                    elif(age == group and group == "8-14 days".title()):
                            eight_14_days += 1  
                    
                    elif(age == group and group == "15-21 days".title()):
                            fifteen_21_days += 1 
                    
                    elif(age == group and group == "22-28 days".title()):
                            twentytwo_28_days += 1 
                    
                    elif(age == group and group == "29-365 days".title()):
                            twentynine_365 += 1 
                    
                    elif(age == group and group == "366-1825 days".title()):
                            threesixsix_1825 += 1 
                    
                    elif(age == group and group == "maternity".title()):
                            maternity += 1 
                            
            
    data.append(stillbirth if stillbirth > 0 else None)
    data.append(zero_one_days if zero_one_days > 0 else None)
    data.append(two_three_days if two_three_days > 0 else None)
    data.append(four_seven_days if four_seven_days > 0 else None)
    data.append(eight_14_days if eight_14_days > 0 else None)
    data.append(fifteen_21_days if fifteen_21_days > 0 else None)
    data.append(twentytwo_28_days if twentytwo_28_days > 0 else None)
    data.append(twentynine_365 if twentynine_365 > 0 else None)
    data.append(threesixsix_1825 if threesixsix_1825 > 0 else None)
    data.append(maternity if maternity > 0 else None)
    
        
    return data
    

def get_death_by_month_data(startDate, endDate, death_date_and_age_container):
    groups = get_age_groups_list()
    months = get_months_object_list(startDate, endDate)
    data = []
    
    for group in groups:
        group = group.title()
        data.append({
                    "name": group,
                    "data": get_group_count_per_month_data(group, months, death_date_and_age_container),
                })
        
    return data
   
    

def get_death_by_month_results(data, startDate, endDate):
    return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Number of deaths by age group per month'.title()
                },
                "xAxis": {
                    "categories": get_months_list(startDate, endDate)
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 16,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
    
    return results


def get_group_count_per_month_data(group, months, death_date_and_age_container):
    data = [] 
    bucket = {}   
    reodered_months = []
    
    for month in months:
        mon = month[0]
        yr = month[1]
        mydate = str(mon) + str(yr)
        unique_key = mydate + group
        reodered_months.append(mydate)  # rearrange months so that months map data in array
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
        
        for cont in death_date_and_age_container:
                row_date = cont[1] + ", " + str(cont[2])
                row_date = row_date.replace(" ", "")
                row_date = row_date.replace(",", "")
                if(row_date == mydate and group == cont[0]):
                    bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for dt in reodered_months:
        for bk in bucket:
            if(bk.startswith(dt)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts




def get_age_at_death_data(age_in_days_container):
    
    groups = get_age_groups_list()
    
    # counts = Counter(age_in_days_container)
    values = {}
    ages_labels = []
    data = []
    for group in groups:
        group = group.title()
        if(not values.has_key(group)):
             values[group] = []
        for age_details in age_in_days_container:
            #if(is_chart_candidate(group, age_details[0])):
            if(group == age_details[0]):
                values[group].append(1)
        

#
    keys_array = []     
    for key in values:
        count = len(values[key])
        keys_array.append(count)
        c = len(values[key])
        elem = [key, c if c > 0 else None]
        data.append(elem)
        

    return data



def get_age_at_death_results(data):
    return {
        "chart": {
             "width":600,
             "height":600,
             "type": 'pie',
                "options3d": {
                    "enabled": "true",
                    "alpha": 45,
                    "beta": 0
                }
        },
        "title": {
            "text": 'Age at death'.title()
        },
        "tooltip": {   
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '{series.name}: <b>{point.y}</b><br/>Porportion: <b>{point.percentage:.1f}%</b></a>'
        },
        
        "plotOptions": {
            "pie": {
                "allowPointSelect": "true",
                "cursor": 'pointer',
                "depth": 30,
                "dataLabels": {
                    "enabled": "true",
                    # "format": '<b>{point.name}</b>: {point.percentage:.1f}%',
                },
               
                "showInLegend": "true"
            }
        },
        "series": [{
            "name": 'Death Count',
            "data": data,
        }],
    }
    

def get_cause_of_death_by_location_data(location_cause_container, unique_causes, unique_locations):
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_location_count_per_cause_data(cause, unique_locations, location_cause_container),
                })
        
    return data

def get_deaths_by_duration_of_illness_data(cause_and_duration_container, unique_causes):
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_duration_count_per_cause_data(cause, cause_and_duration_container),
                })
        
    return data

def  get_cause_of_death_by_location_results(data, unique_locations):
    return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Cause of death by location'.title()
                },
                "xAxis": {
                    "categories": unique_locations
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                

                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data,
            
            
            
            }
    
    return results


def get_location_count_per_cause_data(cause, unique_locations, location_cause_container):
    data = [] 
    bucket = {}   
    reodered_locations = []
    
    for location in unique_locations:
        unique_key = location + cause
        reodered_locations.append(location)  # rearrange locations so that so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in location_cause_container:
            row_location = cont[0] 
            row_cause = cont[1]
            thiskey = row_location + row_cause
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for loc in reodered_locations:
        for bk in bucket:
            if(bk.startswith(loc)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts
    



def  get_duration_count_per_cause_data(cause, cause_and_duration_container):
    data = [] 
    bucket = {}   
    durations = get_duration_of_illness_list()
    reodered_durations = []
    
    for duration in durations:
        unique_key = duration + cause
        reodered_durations.append(duration)  # rearrange duration so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in cause_and_duration_container:
            row_cause = cont[0]
            row_duration = cont[1] 
            thiskey = row_duration + row_cause
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for dur in reodered_durations:
        for bk in bucket:
            if(bk.startswith(dur)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts


def  get_deaths_by_duration_of_illness_results(data):
    return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Number of deaths by duration of illness'.title()
                },
                "xAxis": {
                    "categories": get_duration_of_illness_list()
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
    
    return results



def get_deaths_by_distance_to_hf_data(distance_and_formtype_container, unique_form_types):
    data = []
    
    for type in unique_form_types:
        data.append({
                    "name": type,
                    "data": get_distance_count_per_type_data(type, distance_and_formtype_container),
                })
        
    return data

def get_distance_count_per_type_data(type, distance_and_formtype_container):
    data = [] 
    bucket = {}   
    distances = get_distance_from_hf_list()
    reodered_distances = []
    
    for distance in distances:
        unique_key = distance + type
        reodered_distances.append(distance)  # rearrange duration so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in distance_and_formtype_container:
            row_type = cont[0]
            row_distance = cont[1].strip()
            thiskey = row_distance + row_type
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for dis in reodered_distances:
        for bk in bucket:
            if(bk.startswith(dis)):
                c = len(bucket[bk]) 
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts

    
def get_deaths_by_distance_to_hf_results(data):
     return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Number of Deaths, by distance to health facility'.title()
                },
                "xAxis": {
                    "categories": get_distance_from_hf_list()
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
     
     return results
 
def get_deaths_by_social_reason_and_cause_data(social_and_cause_container, unique_causes, unique_social):
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_reason_count_per_cause_data(cause, unique_social, social_and_cause_container),
                })
        
    return data

def get_reason_count_per_cause_data(cause, unique_social, social_and_cause_container):
    data = [] 
    bucket = {}   
    reodered_social = []
    
    for social in unique_social:
        unique_key = social + cause
        reodered_social.append(social)  # rearrange locations so that so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in social_and_cause_container:
            row_social = cont[0] 
            row_cause = cont[1]
            thiskey = row_social + row_cause
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for soc in reodered_social:
        for bk in bucket:
            if(bk.startswith(soc)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts

def get_deaths_by_social_reason_and_cause_results(data, unique_reasons):
     return {
            
                "chart": {
                    "type": 'bar',
                     "width":670,
                     "height":600,
                     "spacingLeft": 0,
                },
                "title": {
                    "text": 'Social Determinants of Death - by Cause'.title()
                },
                "xAxis": {
                    "categories": unique_reasons
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 14,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "bar": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
     
     return results
 
def get_deaths_by_social_reason_and_village_data(social_and_village_container, unique_villages, unique_social):
    data = []
    
    for village in unique_villages:
        data.append({
                    "name": village,
                    "data": get_reason_count_per_village_data(village, unique_social, social_and_village_container),
                })
        
    return data 


def get_reason_count_per_village_data(village, unique_social, social_and_village_container):
    data = [] 
    bucket = {}   
    reodered_social = []
    
    for social in unique_social:
        unique_key = social + village
        reodered_social.append(social)  # rearrange locations so that so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in social_and_village_container:
            row_social = cont[0] 
            row_village = cont[1]
            thiskey = row_social + row_village
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for soc in reodered_social:
        for bk in bucket:
            if(bk.startswith(soc)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts


def get_deaths_by_social_reason_and_village_results(data, unique_social):
    return {
            
                "chart": {
                    "type": 'bar',
                    "width":675,
                    "height":600,
                    "spacingLeft": 50,
                },
                "title": {
                    "text": 'Social Determinants of Death - by Village'.title()
                },
                "xAxis": {
                    "categories": unique_social
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 14,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "bar": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
     
    return results


def get_deaths_by_prob_accessing_care_data(problems_and_cause_container, unique_causes, unique_problems):
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_problem_count_per_cause_data(cause, unique_problems, problems_and_cause_container),
                })
        
    return data 


def get_problem_count_per_cause_data(cause, unique_problems, problems_and_cause_container):
    data = [] 
    bucket = {}   
    reodered_problems = []
    
    for problem in unique_problems:
        unique_key = problem + cause
        reodered_problems.append(problem)  # rearrange locations so that so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in problems_and_cause_container:
            row_cause = cont[0] 
            row_problem = cont[1]
            thiskey = row_problem + row_cause
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for prob in reodered_problems:
        for bk in bucket:
            if(bk.startswith(prob)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts


def get_deaths_by_prob_accessing_care_results(data, unique_problems):
    return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": ' Number of deaths reporting problems of accessing care'.title()
                },
                "xAxis": {
                    "categories": unique_problems
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
     
    return results
    

def get_facility_where_care_received_data(facilities, facility_care_container):
    values = {}
    data = []
    for facility in facilities:
        if(not values.has_key(facility)):
             values[facility] = []
        for facility_details in facility_care_container:
            if(facility == facility_details[1]):
                values[facility].append(1)
        

#
    keys_array = []     
    for key in values:
        count = len(values[key])
        keys_array.append(count)
        c = len(values[key])
        elem = [key, c if c > 0 else None]
        data.append(elem)
        

    try:
        max_value = max(keys_array)
        max_index = keys_array.index(max_value)
    except:
        max_value = 0
        max_index = 0
     
    if(len(data) > 0):  
        data[max_index] = {
                    "name":data[max_index][0],
                    "y": data[max_index][1],
                    "sliced": "true",
                    "selected": "true"
                }

    # raise Http404(str(data[max_index][0]))  
    return data



def get_facility_where_care_received_results(data):
    return {
        "chart": {
             "width":600,
             "height":600,
             "type": 'pie',
                "options3d": {
                    "enabled": "true",
                    "alpha": 45,
                    "beta": 0
                }
        },
        "title": {
            "text": 'Facility where care was received'.title()
        },
        "tooltip": {
            "headerFormat": "<b>{point.key}</b><br/>",
            "pointFormat": '{series.name}: <b>{point.y}</b><br/>Porportion: <b>{point.percentage:.1f}%</b>'
        },
        "plotOptions": {
            "pie": {
                "allowPointSelect": "true",
                "cursor": 'pointer',
                "depth": 30,
                "dataLabels": {
                    "enabled": "true",
                     "format": '<b>{point.name}</b>',
                },
                "showInLegend": "true"
            }
        },
        "series": [{
            "type": 'pie',
            "name": 'Death Count',
            "data":data,
        }]
    }


def get_cases_treated_at_facility_data(facility_care_container, unique_causes, unique_treated):
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_facility_count_per_cause_data(cause, unique_treated, facility_care_container),
                })
        
    return data 

def get_facility_count_per_cause_data(cause, unique_treated, facility_care_container):
    data = [] 
    bucket = {}   
    reodered_treated = []
    
    for treated in unique_treated:
        unique_key = treated + cause
        reodered_treated.append(treated)  # rearrange locations so that so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in facility_care_container:
            row_treated = cont[0]
            row_cause = cont[2] 
            thiskey = row_treated + row_cause
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for treat in reodered_treated:
        for bk in bucket:
            if(bk.startswith(treat)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts

    
def get_cases_treated_at_facility_results(data, unique_treated):
     return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Number of cases treated at health facility/post or hospital prior to death'.title()
                },
                "xAxis": {
                    "categories": unique_treated
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                     "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
     
     return results
  
    
def get_cases_treated_by_chw_data(case_treated_by_chw_container, unique_causes, unique_cases_treated_by_chw):
    data = []
    
    for cause in unique_causes:
        data.append({
                    "name": cause,
                    "data": get_chw_treated_count_per_cause_data(cause, unique_cases_treated_by_chw, case_treated_by_chw_container),
                })
        
    return data 


def get_chw_treated_count_per_cause_data(cause, unique_cases_treated_by_chw, case_treated_by_chw_container):
    data = [] 
    bucket = {}   
    reodered_treated = []
    
    for treated in unique_cases_treated_by_chw:
        unique_key = treated + cause
        reodered_treated.append(treated)  # rearrange locations so that so that the original order is maintained
        if(not bucket.has_key(unique_key)):
             bucket[unique_key] = []
            
        for cont in case_treated_by_chw_container:
            row_treated = cont[0]
            row_cause = cont[1] 
            thiskey = row_treated + row_cause
            
            if(unique_key == thiskey):
                bucket[unique_key].append(1)
        
    
    counts = []
    
    # count data items putting them in the corrent order
    for treat in reodered_treated:
        for bk in bucket:
            if(bk.startswith(treat)):
                c = len(bucket[bk])
                counts.append(c if c > 0 else None)
                
    # raise Http404(str(len(months)) + "---" + str(len(bucket)) + "---" + str(counts))
    return counts

    
def get_cases_treated_by_chw_results(data, unique_cases_treated_by_chw):
     return {
            
                "chart": {
                    "type": 'column',
                     "width":600,
                     "height":600,
                },
                "title": {
                    "text": 'Number Of Cases Seen By A CHW Prior To Death'
                },
                "xAxis": {
                    "categories": unique_cases_treated_by_chw
                },
                "yAxis": {
                    "min": 0,
                    "title": {
                        "text": 'Number of deaths'.title()
                    },
                "stackLabels": {
                "enabled": "true",
                "style": {
                    "fontWeight": 'bold',
                    "font-size": 18,
                    "textShadow": 'none',
                    "color": '#716D6A' #"(Highcharts.theme && Highcharts.theme.textColor) || 'gray'"
                }
            }
                },
                "tooltip": {
                    "headerFormat": "<b>{point.key}</b><br/>",
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.percentage:.0f}%)<br/>',
                    "shared": "true"
                },
                "plotOptions": {
                    "column": {
                        "stacking": 'normal',
                        "dataLabels": {
                            "enabled": "true",
                            "style": {
                                "textShadow": '0 0 3px black'
                            }
                        }
                    }
                },
                "series": data
            
            
            }
     
     return results

