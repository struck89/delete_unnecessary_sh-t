# -*- coding: utf-8 -*-
"""
Created on Mon Aug 08 09:24:10 2016

@author: eta2
"""

import time
import os
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
    for FILE,size in dictfilesize.iteritems():
        # If extensions list is empty
        if size>threshold and not extensions:
            hugefiles.append(FILE)
        # If extensions list is NOT empty:
        elif size>threshold and extensions:
            if FILE[-3:] in extensions:
                hugefiles.append(FILE)
    return hugefiles

def isdict(a):
    if isinstance(a,dict):
        return True
    else:
        return False
#    try:
#        b=a.copy()
#        b['fdsfgrsdgsrgr']=1
#        return True
#    except:
#        return False

def islist(a):
    if isinstance(a,list):
        return True
    else:
        return False
#    try:
#        b=a[:]
#        b.append('gfdgsdfgdf')
#        return True
#    except:
#        return False

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
        if FILE[-3:] in extensions:
            os.remove(FILE)
            return True
        else:
            return False

#%% 
#rootf='D:/Temp/'
rootf='//filer2sim/cs/techmark/eta2'
extensions=['mdl','stt','pac','res','abq']
i=0
while True:
    i+=1
    alldirs=[rootf]
    foldersin(rootf,alldirs)
    
    allfilesdict=getfilesnsizes(alldirs)
    hugefiles=gethugespecificfiles(allfilesdict,50,extensions)
#    morethan1bytefiles=gethugespecificfiles(allfilesdict,0)
    
    time.sleep(10)
#    gotbigger=getfilesthatgotbigger(allfilesdict,morethan1bytefiles)
    samesized=getfilesthatdidntchangesize(allfilesdict,hugefiles)
    # Code with "safety features" to avoid huge mistakes.
    # We check for the extensions twice.
    # We give more time to the computer to write to a file, is samesized2 has 
    # one file less, it means that that one is still being written on
    if samesized:
        time.sleep(50)
        samesized2=getfilesthatdidntchangesize(allfilesdict,hugefiles)
        for FILE in samesized:
            if FILE in samesized2:
                #Remove can remove many files in a list. For now it seems safer
                #to give a call to the function one file at a time.
                if remove([FILE],extensions):
                    with open('D:/users/eta2/deletedfiles.txt','a') as f:
                        sentence="At "+\
                            str(datetime.now())[:-3]+\
                            ", %4dMB"%allfilesdict[FILE]+\
                            " were freed by deleting "+FILE
                        f.write(sentence+'\n')
                else:
                    sentence="Error with file "+FILE
                    print sentence
                    with open('D:/users/eta2/deletedfiles.txt','a') as f:
                        f.write(sentence+'\n')
                    