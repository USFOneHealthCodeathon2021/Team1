from django.db import models
from django.forms import ModelForm
from django.core.files import File

class Annotation(models.Model):
    #username = models.CharField(max_length=255)
    #project_num = models.DecimalField(max_digits=5,decimal_places=2)
    #TAXON_CHOICES=[
     #  ("eukaryotes","Eukaryotes"),
     #  ("prokaryotes","Prokaryotes"),
     #  ("virus","Virus"),
    #]
    datafile = models.FileField()
    #species= models.CharField(max_length=20,choices=TAXON_CHOICES, default="prokaryotes")
    unique_code = models.CharField(max_length=200, default="123456@codeathon")
    
    annotation_result = models.FileField()
    
    def add_annotation_result(self, result_path, result_name):

        with open (result_path, "rb")as f:
             wrapped_file = File(f)
             self.annotation_result.save(result_name, wrapped_file, save=True)
       
    def __str__(self):
        return self.unique_code


    
