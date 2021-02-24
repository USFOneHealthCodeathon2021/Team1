from django.forms import ModelForm, widgets
from .models import Annotation
from django import forms

#TAXON_CHOICES=(
 #   ("eukaryotes","Eukaryotes"),
  #  ("prokaryotes","Prokaryotes"),
   # ("virus","Virus"),
#)
class HomeForm(ModelForm):
     
     class Meta:
         model = Annotation
         fields = ['datafile', 'unique_code']
         
     #OPTIONS = (("prokka","PROKKA (Prokaryote)"),("rasttk","RASTtk (Prokaryote)"),("pgap","PGAP (Prokaryote)"),("companion","Companion (Eukaryote)"),("gal","GAL (Eukaryote)"),("gaap","GAAP (Eukaryote)"),("vadr","VADR (Virus)"),("vapid","VAPiD (Virus)"))
     #tools = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=OPTIONS, label="Tools")
     user_email=forms.EmailField(max_length=200)
     

class UniquecodeForm(forms.Form):
     uniquecode=forms.CharField(max_length=200)

#class HomeForm(forms.Form):
 #   subject = forms.CharField(max_length=100)
  #  message = forms.CharField(widget=forms.Textarea)
   # sender = forms.EmailField()
   # cc_myself = forms.BooleanField(required=False)
