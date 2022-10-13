from multiprocessing.sharedctypes import Value
from operator import index
import pandas as pd
import json
from pytesseract import pytesseract 
import urllib.request
from PIL import Image
import requests
import cv2 
import numpy as np
import re
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

data = pd.read_json("data.json")

path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe' #creating the pytesseract path
pytesseract.tesseract_cmd = path_to_tesseract

def process_img(s):  #function for processing image and making it the most suitable for pytesseract to work on
    image = cv2.imread('test.jpeg')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # transform to grayscale
    blur = cv2.GaussianBlur(gray_image, (3,3), 0)   #blurring the image
    threshold =  cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=1)
    img_erosion = cv2.erode(opening, kernel, iterations=1)
    img_dilation = cv2.dilate(img_erosion, kernel, iterations=1)
    invert = 255 - img_dilation
    clean_image=pytesseract.image_to_string(s)  #contains the string of extracted text from the cleaned image
    return clean_image

compile=[]
for i in data.iloc[:50,0]:
    r=requests.get(i)       #opening the URL provided in the data base
    with open('test.jpeg','wb') as f:
        f.write(r.content)
    img=Image.open('test.jpeg')
    incoming = process_img('test.jpeg')
    compile.append([incoming])      #contains all the text extracted from the image as a list



img_data=pd.DataFrame(compile)          #converting the list into a dataframe
img_data.columns=["text_from_image"]

                      
def find_date(string):          #implementing regex to get the required date from the text
    regex = r"((19|20)?\d{1,2}\s?[-/]\s?\d{1,2}\s?[-/]\s?(19|20)?\d{2})|"\
    r"((Jan|Feb|Mar|Apr|May|Jun|June|Jul|Aug|Sept|Sep|Oct|Nov|Dec)"\
    r"\s?\d{1,2}\s?[,']?\s?(19|20)?\d{2})|(\d{1,2}\s?[-/]?\s?"\
    r"(Jan|Feb|Mar|Apr|May|Jun|June|Jul|Aug|Sept|Sep|Oct|Nov|Dec)"\
    r"\s?[',-/]?\s?(19|20)?\d{1,2})"
    pattern = re.compile(regex, flags=re.IGNORECASE)
    matches = list(re.finditer(pattern, string))
    if len(matches)==0:
        return None
    date = matches[0].group(0)
    return date


date_dict={}        #date information
for i in img_data.index:    
    string = img_data['text_from_image'][i]
    date=find_date(string)
    date_dict[i]=date #creating a dictionary with key as index and value as time extracted from the text


def uniform_time(string):       #this function is used to get time in different formats into a single datetime.datetime format for easy operations
    if string==None:
        return
    for fmt in ("%d/%m/%Y","%d %b '%y","%d %b %Y","%d-%b-%y","%b %d, %Y","%Y %m %d","%d-%m-%Y"):
        try:
            return datetime.strptime(string,fmt)
        except ValueError:
            continue

#for text information about the expiry duration
for i,j in date_dict.items():
    D=uniform_time(j)
    date_dict[i]=D
print(date_dict)    #a dictionary with index as keys and datetime.datetime as value

d1=datetime.now()
for i,j in date_dict.items():
    d2=j
    try:
        delta=d2-d1     #difference between todays date and the date extracted from the text
        if delta.days>=0: #future expiry
            date_dict[i]=d2 #simply storing in the original dictionary
        else:
            a=data['whatsub_plan']
            dur=a[i]['duration']
            type=a[i]['duration_type']
            if type in ["month","months","Month","Months"]:     #if plan duration is Months then adding the required number of months
                DATE=d2+relativedelta(months=dur)
                date_dict[i]=DATE
            elif type in ["year","years","Year","Years"]:       #if plan duration is years then adding the required number of years
                DATE=d2+relativedelta(years=dur)
                date_dict[i]=DATE
    except:
        continue
    
print()
print(date_dict)

count=0
j=0
for i in data.iloc[:50,1]:
    if date_dict[j]==i:
        count+=1
    j+=1
print("Accuracy ", (count/20)*100)