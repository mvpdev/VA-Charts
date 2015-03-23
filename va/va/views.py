from django.shortcuts import render_to_response
import random, time, string
from __builtin__ import str
from genericutils import *
from reportsutils import *
from va.models import *
from forms import *
from django.conf import settings  # import the settings file
from django.template.response import TemplateResponse
# import generic views
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
# import emailing library
from django.core.mail import EmailMessage


# Users
class UsersView(ListView):
    title = 'Users List'
    template_name = 'users.html'
    model = Users.objects.all()
    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name, {'title': self.title, 'object_list': self.model})


class UsersCreate(CreateView):
    template_name = 'create.html'
    model = Users
    form_class = UsersForm
    title = 'Create User'
    
    success_url = '/users'
    
    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, self.template_name, {'title': self.title, 'object_list': self.model, 'form': self.form_class})
    
    def form_valid(self, form_class):
        try: 
            s = string.lowercase + string.digits
            password = ''.join(random.sample(s, 10))
            user = User.objects.create_user(form_class.cleaned_data['emailaddress'], form_class.cleaned_data['emailaddress'], password)
            user.first_name = form_class.cleaned_data['firstname']
            user.last_name = form_class.cleaned_data['lastname']
            if(form_class.cleaned_data['usertype'] == 1):
                user.is_staff = 1
            user.save()
            
            form_class.instance.authid = user
            name = form_class.cleaned_data['firstname'] + ' ' + form_class.cleaned_data['lastname']
            username = form_class.cleaned_data['emailaddress']
            message = ''' <span style="font-family:Trebuchet MS, Verdana, Arial; font-size:17px; font-weight:bold;">Hello ''' + name + '''!</span>
                            <br /> <p>Your account has been created with the below details:
                            <div style="padding-left:20px; padding-bottom:10px;">-&nbsp;&nbsp;&nbsp;Username - ''' + username + '''</div>
                            <div style="padding-left:20px; padding-bottom:10px;">-&nbsp;&nbsp;&nbsp;Password - ''' + password + '''</div>
                            <p>Kindly follow this link (''' + settings.SYSTEM_URL + ''' ) by clicking or pasting on your browser to access the system.</p>
                            <p>You are advised to change your password after logging in for the first time for security purpose. </p>'''
                        
            email = EmailMessage('VA Reports - User Account Information', message, to=[form_class.cleaned_data['emailaddress']]) 
                        
            email.content_subtype = 'html'
            email.send()
            return super(UsersCreate, self).form_valid(form_class) 
        except Exception, e:
            # raise Http404("Error Creating Account. Please try again or contact the administrator" + str(e))
            return render_to_response('create.html', {'title': self.title, 'form':form_class, 'user': self.request.user, 'err': str(e)})
   

class UpdateUsers(UpdateView):
    template_name = 'update.html'
    model = Users
    form_class = UsersForm
    success_url = '/matcher/users'
    
class DeleteUsers(DeleteView):
    model = Users
    template_name = 'user_delete.html'  
    
    def get_success_url(self):
        return reverse_lazy('users_index')




# Sites
class SitesView(ListView):
    title = 'Sites List'
    template_name = 'sites.html'
    model = Sites
    
#     def get(self, request, *args, **kwargs):
#         return TemplateResponse(request, self.template_name, {'title': self.title, 'object_list': self.model})

class SitesCreate(CreateView):
    template_name = 'create.html'
    model = Sites
    form_class = SitesForm
    success_url = '/sites'
    
        
    def form_valid(self, form_class):
        form_class.instance.datakey = str(form_class.instance.name).strip().lower().replace(" ", "_") + "_redis_cache"
        return super(SitesCreate, self).form_valid(form_class) 
    


class UpdateSites(UpdateView):
    template_name = 'update.html'
    model = Sites
    success_url = '/sites'
    
class DeleteSites(DeleteView):
    model = Sites
    template_name = 'site_delete.html'  
    
    def get_success_url(self):
        return reverse_lazy('sites_index')


def index(request):     
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    site_data = pickle.loads(r.get('ruhiira_data'))
    data = dispatch_report(site_data, request)    
    data.update({'mydata': {
                    'name': 'Joe',
                    'data': [3, 4, 4, 2, 5]
                },
                 'mydata2': {
                    'name': 'Josiah',
                    'data': [7, 4, 3, 2, 5]
                }})
    
    return render_to_response('reports.html', data)

def home(request):
    data = initialize_data(request)
    return render_to_response('home.html', data)
