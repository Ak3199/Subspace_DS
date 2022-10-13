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

data = pd.read_json("data.json")
#print(df)

path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.tesseract_cmd = path_to_tesseract

def process_img(s): 
    image = cv2.imread('test.jpeg')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # transform to grayscale
    blur = cv2.GaussianBlur(gray_image, (3,3), 0)
    threshold =  cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=1)
    img_erosion = cv2.erode(opening, kernel, iterations=1)
    img_dilation = cv2.dilate(img_erosion, kernel, iterations=1)
    invert = 255 - img_dilation
    clean_image=pytesseract.image_to_string(s)
    return clean_image

compile=[]

for i in data.iloc[:5,0]:
    r=requests.get(i)
    with open('test.jpeg','wb') as f:
        f.write(r.content)
    img=Image.open('test.jpeg')
    incoming = process_img('test.jpeg')
    compile.append([incoming])
#print(compile)


img_data=pd.DataFrame(compile) #the dataframe containing all the image text
img_data.columns=["text_from_image"]
#print(img_data)
                      

# def date_extract(df):
#      # 04/20/2009; 04/20/09; 4/20/09; 4/3/09
#     search1 = dict()
#     for ind,vals in dict(df.apply(lambda x:re.search('\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',x))).items():
#         search1[ind]=vals  #.groups()

#     # Mar-20-2009; Mar 20, 2009; March 20, 2009; Mar. 20, 2009; Mar 20 2009;
#     search2 = dict()
#     for ind,vals in dict(df.apply(lambda x:re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z.,-]*[\s-]?(\d{1,2})?[,\s-]?[\s]?\d{4}',x,re.I|re.M))).items():
#         search2[ind]=vals       #.group()
            
#     date_series = pd.concat([pd.Series(search1),pd.Series(search2)])
#     print(date_series)


# date_extract(img_data)

def date_extract(index,string):
    # 04/20/2009; 04/20/09; 4/20/09; 4/3/09
    search1={}
    extract=re.search(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", string)
    if extract:
        search1[index]=extract
    
    
    # Mar-20-2009; Mar 20, 2009; March 20, 2009; Mar. 20, 2009; Mar 20 2009;
    search2={}
    extract=re.search(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-zA-Z.,-]*[\s-]?(\d{1,2})?[,\s-]?[\s]?\d{4}",string,re.I|re.M)
    if extract:
        search2[index]=extract
        
    #dd MM yyyy
    search3={}
    extract=re.search(r"[\d]{1,2} [ADFJMNOS]\w* [\d]{4}", string)
    if extract:
        search3[index]=extract
    
    date_series=pd.concat(pd.DataFrame(search1),pd.DataFrame(search2),pd.DataFrame(search3))
    return date_series

for i in img_data.index:
    string = img_data['text_from_image'][i]
    DF=date_extract(i,string)

print(DF)

    
    
    






    

  