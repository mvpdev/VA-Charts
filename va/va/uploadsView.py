from django.shortcuts import render_to_response
from reportsutils import *
# import generic views
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View

def index(request):
    data = data = initialize_data(request)
    
    
    return render_to_response('uploads/index.html', data)

class RawDataFilesCreate(CreateView):
    template_name = 'create.html'
    model = RawDataFiles
    form_class = RawDataFilesForm
    
    success_url = '/data/upload'
    
    def form_valid(self, form_class):
         user = getCurrentUser(self.request.user.id)
         form_class.instance.uploadedby = user
         return super(RawDataFilesCreate, self).form_valid(form_class) 

    
#uploads view
class RawDataFilesView(ListView):
    title = 'Uploads List'
    template_name = 'uploads/index.html'
    model = RawDataFiles
    
    
    
class RawDataFilesUpdate(UpdateView):
    template_name = 'update.html'
    model = RawDataFiles
    form_class = RawDataFilesFormUpdate
    success_url = '/data/upload'
    
