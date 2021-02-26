from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .forms import HomeForm, UniquecodeForm
from .models import Annotation
from django.core.files import File

import os
from mysite.settings import BASE_DIR
tmppath = os.path.join(BASE_DIR, 'media/tmp')

import tarfile
import zipfile

from django.core.mail import send_mail

def homepage(request):
    
    form = HomeForm(request.POST, request.FILES or None)
    if request.method == 'POST':
       if form.is_valid():
          form.save()
          #filepath = form.genomefile.path
          #handle_uploaded_file(request.FILES['genomefile'])
          #species = request.POST.get('species')
          #uploadedgenomefile = request.FILES['genomefile']
          # ? form.id, form.genomefile
          uniquecodeis = request.POST.get('unique_code')
          uploadedgenomeobject = Annotation.objects.get(unique_code=uniquecodeis)
          request.session['uploadedgenomeid'] = uploadedgenomeobject.id
          request.session['uniquecode']=uniquecodeis
          #send unique code to user email
          useremailis = request.POST.get('user_email')
          request.session['useremailis']=useremailis
          if useremailis != 'liulabdellserver@gamil.com':
               send_mail('Your Unique Code','Your unique code is '+uniquecodeis, 'liulabdellserver@gmail.com', [useremailis], fail_silently=False)
          return redirect('annotation')
          #return HttpResponseRedirect('process/')
    return render(request, 'codeathonteam/homepage.html', {'form': form})

def annotation(request):
    fileidis = request.session['uploadedgenomeid']
    uniquecodeis = request.session['uniquecode']
    useremailis = request.session['useremailis']
    annotationobject = get_object_or_404(Annotation, pk=fileidis)
    
    #pipeline function for genome annotation
    pipeline(fileidis, annotationobject.datafile)
    #os.system('bash '+'{}/{}/bashbatch.sh >{}/{}/outlog.txt 2>&1'.format(tmppath,fileidis,tmppath,fileidis))
    
    # storage the annotation results in .zip format into related database by model's method 
    filewithpath = '{}/{}.zip'.format(tmppath,fileidis)
    filenameonly = '{}.zip'.format(fileidis)
    annotationobject.add_annotation_result(filewithpath, filenameonly)
    
    
    
   # filewithpath = '{}/AnnotateResults_{}.zip'.format(tmppath,fileidis)
   # filenameonly = 'AnnotateResults_{}.zip'.format(fileidis)
   # annotationobject.add_annotation_result(filewithpath, filenameonly)
    
    send_mail('Your Annotation Done', 'Your annotation at Integrative Genome Annotation Service has been completed!\nYour Unique Code: '+uniquecodeis+'\nYou can use the unique code to download the annotation result from the link http://127.0.0.1:8000/codeothonteam/process.', 'liulabdellserver@gmail.com', [useremailis], fail_silently=False)
    
    return render(request, 'codeathonteam/annotation.html')
    
    # javascript/jquery should be added for showing running status in the template


def process(request):
    yourcode = UniquecodeForm(request.POST or None)
    if request.method == 'POST':
       if yourcode.is_valid():
          uniquecodeis = request.POST.get('uniquecode')
          annotationfile = Annotation.objects.get(unique_code=uniquecodeis)
          request.session['downloadfileid']=annotationfile.id
          return redirect('download')
          #render(request, 'GAv1/download.html', {'uniquecodeis':uniquecodeis})
    return render(request, 'codeathonteam/processpage.html',{'yourcode':yourcode})

def download(request):
    fileidis = request.session['downloadfileid']
    #downloadedfile = Annotation.objects.get(pk=fileidis)
    downloadedobject = get_object_or_404(Annotation, pk=fileidis)
    return render(request, 'codeathonteam/download.html', {'downloadedobject':downloadedobject})
    
def about(request):
    return render(request, 'codeathonteam/about.html')
def contact(request):
    return render(request, 'codeathonteam/contact.html')
def tutoral(request):
    return render(request, 'codeathonteam/tutoral.html')

###################### not view functions ################################
def pipeline(fileid, file_for_annotation):
    fileidis = fileid
    if not os.path.exists('{}/{}'.format(tmppath,fileidis)):
        os.makedirs('{}/{}'.format(tmppath,fileidis))
    with open('{}/{}/sequence_for_annotation.txt'.format(tmppath,fileidis), 'wb+') as destination:
        for chunk in file_for_annotation.chunks():
            destination.write(chunk)
    
    os.makedirs('{}/{}/prokka'.format(tmppath,fileidis))       

    
    
    with zipfile.ZipFile('{}/{}.zip'.format(tmppath,fileidis), 'w', ) as myzip:
         for root, dirs, files in os.walk('{}/{}'.format(tmppath,fileidis)):
            for onefile in files:
                onefile_with_path = os.path.join(root, onefile)
                myzip.write(onefile_with_path, arcname = os.path.basename(onefile_with_path))
               

