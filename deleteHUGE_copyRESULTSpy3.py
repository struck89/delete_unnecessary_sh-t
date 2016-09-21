# -*- coding: utf-8 -*-
"""
Created on Mon Aug 08 09:24:10 2016

@author: eta2
"""

import os
import time
import shutil
from datetime import datetime

def foldersin(currentpath,alldirs):
    """ Modifies the list 'alldirs' by appending all the folders in
    currentpath. It goes as deep as possible by calling itself on every 
    new folder it finds on currentpath
    Discards the folders where we have no access """
    if (currentpath[-1]=='/' or currentpath[-1]=='\\'):
        currentpath=currentpath[:-1]
    #let's try if we can enter such folder
    try:
        candidates=os.listdir(currentpath+'/')
    except:
        #If we can't enter, then there's nothing inside for us.
        alldirs.remove(currentpath)
        candidates=[]
    newdirs=[]
    for candidate in candidates:
#        print candidate
        if os.path.isdir(currentpath+'/'+candidate):
#            print currentpath+'/'+candidate
            newdirs.append(currentpath+'/'+candidate)
            alldirs.append(currentpath+'/'+candidate)
    for newdir in newdirs:
        foldersin(newdir,alldirs)

def getfilesnsizes(folders):
    """ Returns a dict given a list of folders,
    the key being the file with its full path, 
    the value its size in MB"""
    dictfilesize={}
    for folder in folders:
        try:
            candidates=os.listdir(folder)
        except:
            candidates=[]
        for candidate in candidates:
            if not os.path.isdir(folder+'/'+candidate):
                try:
                    filesize=os.path.getsize(folder+'/'+candidate)
                    filesize=float(filesize)/1024**2
                except:
                    #something weird happened. We should never enter here
                    filesize=-1
                dictfilesize[folder+'/'+candidate]=filesize
    return dictfilesize

def gethugespecificfiles(dictfilesize,threshold=100,extensions=[]):
    """ Returns the files that are above a certain size threshold"""
    hugefiles=[]
    for FILE,size in dictfilesize.items():
        # If extensions list is empty
        if size>threshold and not extensions:
            hugefiles.append(FILE)
        # If extensions list is NOT empty:
        elif size>threshold and extensions:
            if FILE[-3:] in extensions:
                hugefiles.append(FILE)
    return hugefiles

#def isdict(a):
#    return isinstance(a,dict)
#
#def islist(a):
#    return isinstance(a,list)

def getfilesthatgotbigger(dictofprevsizes,listoffilestocheck):
    biggerfiles=[]
    for FILE in listoffilestocheck:
        if FILE in dictofprevsizes:
            filesize=os.path.getsize(FILE)
            filesize=float(filesize)/1024**2
            if filesize>dictofprevsizes[FILE]:
                biggerfiles.append(FILE)
    return biggerfiles

def getfilesthatdidntchangesize(dictofprevsizes,listoffilestocheck):
    samesized=[]
    for FILE in listoffilestocheck:
        if FILE in dictofprevsizes:
            filesize=os.path.getsize(FILE)
            filesize=float(filesize)/1024**2
            if filesize==dictofprevsizes[FILE]:
                samesized.append(FILE)
    return samesized

def remove(files,extensions):
    for FILE in files:
        try:
            if FILE[-3:] in extensions:
                os.remove(FILE)
                return True
            else:
                return False
        except:
            return False

def getfoldersthathavefinishedruns(folders,required_file_ext,minutes_ago=60):
    folders_to_move=[]
    for folder in folders:
        files=os.listdir(folder)
        required_inside=0
        log_file=''
        for FILE in files:
            if FILE[-4:].lower() in required_file_ext:
                required_inside+=1
                if FILE[-4:]=='.log':
                    log_file=log_file+FILE
        if len(required_file_ext)==required_inside and onlyonejob(folder):
            with open(folder+'/'+log_file,'r') as f:
                raw_data=f.readlines()
            raw_data=[line for line in raw_data if len(line.strip())>1]
            raw_data.reverse()
            if ('COMPLETED' in raw_data[0]):# and ('EDT' in raw_data[-3]):
                for line in raw_data:
                    if 'EDT' in line:
                        break
                when_it_finished=datetime.strptime(\
                line.strip()[:-4],"%a %d %b %Y %I:%M:%S %p")
                delta=datetime.now()-when_it_finished
                if delta.total_seconds()/60. > minutes_ago:
                    folders_to_move.append(folder)
    return folders_to_move

def onlyonejob(folder,get_job_name=False):
    files=os.listdir(folder+'/')
    inps=[FILE for FILE in files if '.inp' in FILE]
    jobs=0
    job=''
    for inp in inps:
        f=open(folder+'/'+inp,'r')
        text=f.read(2000)
        if 'Living Heart Human Model' in text:
            jobs+=1
            job=job+inp
        f.close()
    if jobs==1 and not get_job_name:
        return True
    if jobs==1 and get_job_name:
        return True,job
    if get_job_name:
        return False,''
    else:
        return False

def move_files_to(folder,descr_of_files_to_move,destination):
    folder_name=folder.split('/')[-1].split('\\')[-1]
#    print(folder_name)
    full_destination=destination+'/'+folder_name
    files=os.listdir(folder)
    files_to_move=[]
    for FILE in files:
        if FILE in descr_of_files_to_move:
            files_to_move.append(FILE)
        elif FILE[-4:] in descr_of_files_to_move:
            files_to_move.append(FILE)
    only_one_job,job=onlyonejob(folder,True)
    if only_one_job:
        files_to_move.append(job)
    if len(descr_of_files_to_move)==len(files_to_move):
        try:
            os.mkdir(destination+'/'+folder_name)
            for FILE in files_to_move:
                shutil.move(folder+'/'+FILE,\
                          full_destination+'/'+FILE)
            shutil.rmtree(folder)
            os.remove(full_destination+'/'+'heart-elec-coarse.odb')
            return True
        except Exception as err:
            print('Huge ERROR')
            print(err)
            return False

#%% 
#rootf='D:/Temp/'
rootf='//filer2sim/cs/techmark/eta2'
extensions=['mdl','stt','pac','res','abq']
required_file_ext=['.log','.sta','.dat','.odb','extra_to_account_for_2_odbs']
descr_of_files_to_move=required_file_ext[:]+\
                        ['mech-mat-RA_ACTIVE.inp',
                        'mech-mat-RV_ACTIVE.inp',
                        'mech-mat-LA_ACTIVE.inp',
                        'mech-mat-LV_ACTIVE.inp',
                        'mech-mat-PASSIVE.inp',
                        'extra_to_account_for_job_inp']
destination='D:/users/eta2/autotransfers'
i=0
while True:
    i+=1
    alldirs=[rootf]
    foldersin(rootf,alldirs)
    folders_to_move=getfoldersthathavefinishedruns(alldirs,required_file_ext,10)
    if folders_to_move:
        for folder in folders_to_move:
            if move_files_to(folder,descr_of_files_to_move,destination):
                with open('D:/users/eta2/movedfiles.txt','a') as f:
                    folder_name=folder.split('/')[-1].split('\\')[-1]
                    sentence="%05d"%i+"-At "+\
                        str(datetime.now())[:-3]+\
                        ", the files from "+folder+\
                        " were moved to "+destination+'/'+folder_name
                    f.write(sentence+'\n')

    allfilesdict=getfilesnsizes(alldirs)
    hugefiles=gethugespecificfiles(allfilesdict,50,extensions)
#    morethan1bytefiles=gethugespecificfiles(allfilesdict,0)
    
    time.sleep(30)
#    gotbigger=getfilesthatgotbigger(allfilesdict,morethan1bytefiles)
    samesized=getfilesthatdidntchangesize(allfilesdict,hugefiles)
    # Code with "safety features" to avoid huge mistakes.
    # We check for the extensions twice.
    # We give more time to the computer to write to a file, is samesized2 has 
    # one file less, it means that that one is still being written on
    if samesized:
        time.sleep(120)
        samesized2=getfilesthatdidntchangesize(allfilesdict,hugefiles)
        for FILE in samesized:
            if FILE in samesized2:
                #Remove can remove many files in a list. For now it seems safer
                #to give a call to the function one file at a time.
                if remove([FILE],extensions):
                    with open('D:/users/eta2/deletedfiles.txt','a') as f:
                        sentence="%05d"%i+"-At "+\
                            str(datetime.now())[:-3]+\
                            ", %4dMB"%allfilesdict[FILE]+\
                            " were freed by deleting "+FILE
                        f.write(sentence+'\n')
                else:
                    sentence="%05d"%i+"Error with file "+FILE
                    print(sentence)
                    with open('D:/users/eta2/deletedfiles.txt','a') as f:
                        f.write(sentence+'\n')
                    