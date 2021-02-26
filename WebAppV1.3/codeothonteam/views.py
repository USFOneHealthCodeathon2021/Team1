from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from .forms import HomeForm, UniquecodeForm, UserForm
from .models import Annotation
from django.core.files import File

import os
from mysite.settings import BASE_DIR
tmppath = os.path.join(BASE_DIR, 'media/tmp')
filepath = os.path.join(BASE_DIR, 'media')

import tarfile
import zipfile

from django.core.mail import send_mail

import csv
import pandas as pd
import numpy as np
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import chi2
from collections import defaultdict
import seaborn as sns
from matplotlib import pyplot as plt



def prepage(request):
    return render(request, 'codeathonteam/prepage.html')

def personalinformation(request):

    form2 = UserForm(request.POST, request.FILES or None)
    if request.method == 'POST':
       if form2.is_valid():
          form2.save()
          return redirect('annotation')
    return render(request, 'codeathonteam/personalinformation.html', {'form2':form2})

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

          #get csv files
          #request.session['csvfile'] = request.FILES.get("datafile")
          #csv = request.FILES.get("datafile")
          #print(csv)

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
    #pipeline(fileidis, annotationobject.datafile)
    #os.system('bash '+'{}/{}/bashbatch.sh >{}/{}/outlog.txt 2>&1'.format(tmppath,fileidis,tmppath,fileidis))
    if not os.path.exists('{}/{}'.format(tmppath,fileidis)):
        os.makedirs('{}/{}'.format(tmppath,fileidis))



    ###########  data summary ####################################################
    # get the name of csv file from Database, then use full path to find csv file loacation (Note: in "media" folder)
    csvfilename = Annotation.objects.get(unique_code=uniquecodeis).datafile
    num_samples = 0
    num_features = 0
    cells={}
    with open('{}/{}'.format(filepath,csvfilename), 'r') as csvfile:
        lines = csv.reader(csvfile)
        for row in lines:
            print(row,"\n")
            #print('\t'.join(row))
            if num_samples < 5:
                cells[num_samples] = row
            num_samples += 1
        num_features = len(cells[0])

    ######## Model ##############################################################
    file = pd.read_csv('{}/{}'.format(filepath,csvfilename), encoding='latin1')
    #print(file.head())
    #print(file.isnull().sum())
    filled_file = file.fillna(0)
    #print(filled_file.isna().sum())
    life_threatening  = np.array(filled_file['L_THREAT'])
    hospitalized  = np.array(filled_file['HOSPITAL'])
    disabled = np.array(filled_file['DISABLE'])
    recoved = np.array(filled_file['RECOVD']) # df with more samples
    died = np.array(filled_file['DIED'])

    life_threatening[life_threatening == 0] = 'N'
    hospitalized[hospitalized == 0] = 'N'
    disabled[disabled == 0] = 'N'
    recoved[recoved == 0] = 'N'
    died[died == 0] = "N"
    #print(died)
    # remove the columns that are not needed
    cols = ['L_THREAT', 'HOSPITAL', 'DISABLE', 'RECOVD', 'DIED', 'VAX_TYPE','OFC_VISIT', 'ER_ED_VISIT', 'STATE', 'VAX_SITE']
    df = filled_file.loc[:, ~filled_file.columns.str.contains('|'.join(cols))]
    cat_cols = ['STATE', 'SEX', 'DIED', 'OTHER_MEDS',
           'CUR_ILL', 'HISTORY', 'ALLERGIES', 'SYMPTOM1', 'SYMPTOM2',
            'SYMPTOM3', 'SYMPTOM4', 'SYMPTOM5',
            'VAX_MANU', 'VAX_DOSE_SERIES', 'VAX_ROUTE', 'VAX_SITE',
           'VAX_NAME', 'BIRTH_DEFECT', 'ER_VISIT']
    df_cat = df.loc[:, df.columns.str.contains('|'.join(cat_cols))]
    df_num = df.loc[:, ~df.columns.str.contains('|'.join(cat_cols))]
    #print(df_cat)
    # one hot encoding
    df_dum = pd.get_dummies(df_cat)
    # combine data
    df_final = pd.concat([df_num, df_dum], axis=1)
    # create a dictionary of labels
    labels = dict({'life_threatening': life_threatening,
               'hospitalized': hospitalized,
               'disabled': disabled,
               'recoved': recoved,
               'died': died,
    })
    #print(labels['life_threatening'])
    # Split dataset to select feature and evaluate the classifier
    models_bfs = dict()
    for key in labels:
         with open('{}/{}/all_features_training.txt'.format(tmppath,fileidis),'a') as f:
                 print("Training on ", key, file=f)
         X_train, X_test, y_train, y_test = train_test_split(
              df_final, labels[key], test_size = 0.50,
              random_state=0
         )

         clf = make_pipeline(MinMaxScaler(), LinearSVC(max_iter= 2000))
         clf.fit(X_train, y_train)
         models_bfs[key] = clf
         prediction = clf.predict(X_test)
         with open('{}/{}/all_features_training.txt'.format(tmppath,fileidis),'a') as f:
              print('Classification accuracy before feature selection: {:.3f}\n',classification_report(y_test, prediction), file=f)
         #print('Classification accuracy before feature selection: {:.3f}'.format(clf.score(X_test, y_test)))
    # we will try reducing the features
    class SelectFeatures():

        def __init__(self):

            """
            Function constructor

            """
            self.fit_lis = []
            self.df_imp_lis = []


        def CallFit(self, df, labels, top_fea):
            """
            Fit model for feature selection.
            The model will fit the data to find the predictive
            features for response variable.

            Parameters:
            ----------
            df : List of data frames you want to select features from
            labels : List of response variable.
            top_fea : Number of features you want to select

            """
            top_selected = SelectKBest(score_func = chi2, k = top_fea)
            fit = top_selected.fit(df, labels)
            self.fit_lis.append(fit)



        def UnivFeatureSelection(self, df, index):
            """
            This function will call the fitted models to select the features

            Parameters:
            ----------
            df : List of data frames you want to select features from
            index : Index of the model fitted on the data

            """
            cols = self.fit_lis[index].get_support(indices=True)
            df_impt_uvs = df.iloc[:,cols]
            self.df_imp_lis.append(df_impt_uvs)
            return self.df_imp_lis


    features = np.arange(10, 100, 10)
    models_after_fs = defaultdict(list)
    accuracy = defaultdict(list)
    important_fea = defaultdict(list)
    train_test_imp = defaultdict(list)

    for i, val in enumerate(features):
          if(val % 10 == 0):
              with open('{}/{}/reducing_features.txt'.format(tmppath,fileidis),'a') as f:
                   print("# Features :", val, file=f)
          for key in labels:
              with open('{}/{}/reducing_features.txt'.format(tmppath,fileidis),'a') as f:
                   print(key, file=f)
              FS = SelectFeatures()
              with open('{}/{}/reducing_features.txt'.format(tmppath,fileidis),'a') as f:
                   print(features[i], file=f)
              FS.CallFit(df = df_final,
                   labels = labels[key],
                   top_fea = features[i])
              imp_fea = FS.UnivFeatureSelection(df = df_final, index = 0 )
              important_fea[key].append((val, imp_fea[0]))

              X_train, X_test, y_train, y_test = train_test_split(imp_fea[0],
                                                            labels[key],
                                                            test_size = 0.25,
                                                            random_state = 0)
              train_test_imp[key].append((val, X_train, X_test,
                                    y_train, y_test ))

              clf = make_pipeline(StandardScaler(), SVC(max_iter=2000))
              clf.fit(X_train, y_train)
              prediction = clf.predict(X_test)
              acc = clf.score(X_test, y_test)
              clf_rep = classification_report(y_test, prediction)
              models_after_fs[key].append((val, clf)) # store #feature and models
              with open('{}/{}/reducing_features.txt'.format(tmppath,fileidis),'a') as f:
                   print(clf_rep, file=f)
              with open('{}/{}/reducing_features.txt'.format(tmppath,fileidis),'a') as f:
                   print("Accuracy :{:.3f}" .format(acc), file=f)
              accuracy[key].append((val, acc)) # store #feature and accuracy

    accuracy_df = [(k, *t) for k, v in accuracy.items() for t in v]
    accuracy_df = pd.DataFrame(accuracy_df, columns=['Variable','features_num','accuracy'])
    # get the rows with ms
    idx = accuracy_df.loc[accuracy_df.groupby('Variable')['accuracy'].idxmax()]
    sns.set(font_scale = 1)
    ax = sns.lineplot(
        data=accuracy_df,
        x="features_num", y="accuracy",
        palette=['purple', 'blue', 'grey', 'orange', 'red'],
        hue="Variable"
    )
    ax.set(xlabel='Number of features', ylabel='Accuracy')
    #plt.show()
    plt.savefig('{}/{}/features_vs_accuracy.png'.format(tmppath,fileidis))

    #important_fea['life_threatning'][4][1]
    #important_fea['life_threatning'][4][1].to_csv('{}/{}/Important_features_predicting_Life_threatning_illness.csv'.format(tmppath,fileidis))
    #important_fea['hospitalized'][4][1]
    #important_fea['hospitalized'][4][1].to_csv('{}/{}/Important_features_predicting_Hospitalized.csv'.format(tmppath,fileidis))
    #important_fea['disabled'][4][1]
    #important_fea['disabled'][4][1].to_csv('{}/{}/Important_features_predicting_disabled.csv'.format(tmppath,fileidis))
    #important_fea['recoved'][4][1]
    #important_fea['recoved'][4][1].to_csv('{}/{}/Important_features_predicting_Recovered.csv'.format(tmppath,fileidis))
    #important_fea['died'][4][1]
    #important_fea['died'][4][1].to_csv('{}/{}/Important_features_predicting_Died.csv'.format(tmppath,fileidis))

    ######### generate zip file
    with open('{}/{}/datafile.txt'.format(tmppath,fileidis), 'wb+') as destination:
        for chunk in csvfilename.chunks():
            destination.write(chunk)

    with zipfile.ZipFile('{}/{}.zip'.format(tmppath,fileidis), 'w', ) as myzip:
         for root, dirs, files in os.walk('{}/{}'.format(tmppath,fileidis)):
            for onefile in files:
                onefile_with_path = os.path.join(root, onefile)
                myzip.write(onefile_with_path, arcname = os.path.basename(onefile_with_path))

    ######### storage the annotation results in .zip format into related database by model's method ###########
    filewithpath = '{}/{}.zip'.format(tmppath,fileidis)
    filenameonly = '{}.zip'.format(fileidis)
    annotationobject.add_annotation_result(filewithpath, filenameonly)

   # filewithpath = '{}/AnnotateResults_{}.zip'.format(tmppath,fileidis)
   # filenameonly = 'AnnotateResults_{}.zip'.format(fileidis)
   # annotationobject.add_annotation_result(filewithpath, filenameonly)

    send_mail('Your Annotation Done', 'Your annotation at Integrative Genome Annotation Service has been completed!\nYour Unique Code: '+uniquecodeis+'\nYou can use the unique code to download the annotation result from the link http://127.0.0.1:8000/codeothonteam/process.', 'liulabdellserver@gmail.com', [useremailis], fail_silently=False)

    # show result in webpage
    #f = open('{}/{}/all_features_training.txt'.format(tmppath,fileidis),'r')
    #file1_content=f.read()
    #f.close()

    #f = open('{}/{}/reducing_features.txt'.format(tmppath,fileidis),'r')
    #file2_content=f.read()
    #f.close()

    #output1 = '/media/tmp/{}/all_features_training.txt'.format(fileidis)
    #output2 = '{}/{}/reducing_features.txt'.format(tmppath,fileidis)
    output3 = '/media/tmp/{}/features_vs_accuracy.png'.format(fileidis)
    return render(request, 'codeathonteam/annotation.html', {'num_samples':num_samples, 'num_features':num_features, 'featurename': cells[0], 'output3':output3})

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
    # Load data
    #file = pd.read_csv('{}/{}/sequence_for_annotation.txt'.format(tmppath,fileidis), encoding='latin1')
    #print(file)
    #file.head()
    #file.isnull().sum()
    #filled_file = file.fillna(0)
    #print(filled_file)

    os.makedirs('{}/{}/prokka'.format(tmppath,fileidis))



    with zipfile.ZipFile('{}/{}.zip'.format(tmppath,fileidis), 'w', ) as myzip:
         for root, dirs, files in os.walk('{}/{}'.format(tmppath,fileidis)):
            for onefile in files:
                onefile_with_path = os.path.join(root, onefile)
                myzip.write(onefile_with_path, arcname = os.path.basename(onefile_with_path))
