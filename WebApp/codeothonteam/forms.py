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

     email_notice = forms.BooleanField(required=False)
     user_email=forms.EmailField(max_length=200)


class UniquecodeForm(forms.Form):
     uniquecode=forms.CharField(max_length=200)

class UserForm(forms.Form):
     age=forms.IntegerField(label="Age")
     state=forms.CharField(label="State")
     sex=forms.ChoiceField(choices=((0,'F'),(1,'M'),))
     lthreat=forms.ChoiceField(choices=((0,'Yes'),(1,'No'),))
     hospital=forms.ChoiceField(choices=((0,'Yes'),(1,'No'),))
     disable=forms.ChoiceField(choices=((0,'Yes'),(1,'No'),))
     recovd=forms.ChoiceField(choices=((0,'Yes'),(1,'No'),(2,"Unknown"),))
     numdays=forms.IntegerField(label="Days")
     othermeds=forms.CharField(label="Other Meds")
     curill=forms.CharField(label="Curill")
     curill=forms.CharField(label="Other Meds")
     history=forms.CharField(label="History")
     ofcvisit=forms.ChoiceField(choices=((0,'Yes'),(1,'No'),))
     eredvisit=forms.ChoiceField(choices=((0,'Yes'),(1,'No'),))
     allergies=forms.CharField(label="Allergies")
     symptions=forms.CharField(label="Symptoms")
     vaxtype=forms.CharField(label="vaxtype", initial="COVID19")
     vaxmanu=forms.ChoiceField(choices=((0,'MODERNA'),(1,'PFIZER\BIONTECH'),))
     vaxdoseseries=forms.ChoiceField(choices=((0,'1'),(1,'2'),(2,"Unknown"),))
     vaxroute=forms.ChoiceField(choices=((0,'IM'),(1,'SYR'),(2,'OT'),(3,"Unknown"),))
     vaxsite=forms.ChoiceField(choices=((0,'LA'),(1,'AR'),(2,'RA'),(3,"OT"),(4,"Unknown"),))
     vaxname=forms.ChoiceField(choices=((0,'COVID19 (COVID19 (MODERNA))'),(1,'COVID19 (COVID19 (PFIZER-BIONTECH))'),))



#class HomeForm(forms.Form):
 #   subject = forms.CharField(max_length=100)
  #  message = forms.CharField(widget=forms.Textarea)
   # sender = forms.EmailField()
   # cc_myself = forms.BooleanField(required=False)
