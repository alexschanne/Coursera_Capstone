#!/usr/bin/env python
# coding: utf-8

# <H1> Coursera Capstone- Toronto Neighbourhood Assignment

# This notebook is in response to Coursera Capstone Week 3 assignment. It will utilize Foursquare API and newly acquired skills from the course.

# In[7]:


#getting the imports out of the way
import numpy as np 

import pandas as pd 
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json

get_ipython().system('conda install -c conda-forge geopy --yes')
from geopy.geocoders import Nominatim 

import requests 
from pandas.io.json import json_normalize

import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.datasets.samples_generator import make_blobs

#!conda install -c conda-forge folium=0.5.0 --yes
import folium

#!conda install -c anaconda beautifulsoup4
from bs4 import BeautifulSoup
import requests
import lxml
print('Libraries imported.')


# <H2> Scraping Website

# In[29]:


#linking and scraping website
r= requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M')
soup = BeautifulSoup(r.text, 'lxml')
table= soup.find('table', attrs={'class':'wikitable sortable'})

headers=table.findAll('th')
for i, head in enumerate(headers): headers[i]=str(headers[i]).replace("<th>","").replace("</th>","").replace("\n","")

rows=table.findAll('tr')
rows=rows[1:len(rows)]

for i, row in enumerate(rows): rows[i] = str(rows[i]).replace("\n</td></tr>","").replace("<tr>\n<td>","")

#Creating the Data Frame
df=pd.DataFrame(rows)
df[headers] = df[0].str.split("</td>\n<td>", n = 2, expand = True) 
df.drop(columns=[0],inplace=True)

df=df.drop(df[(df.Borough== "Not assigned")].index)
df.Neighbourhood.replace("Not assigned", df.Borough, inplace=True)

df.Neighbourhood.fillna(df.Borough, inplace=True)
df=df.drop_duplicates()

df.update(
    df.Neighbourhood.loc[
        lambda x: x.str.contains('title')
    ].str.extract('title=\"([^\"]*)',expand=False))

df.update(
    df.Borough.loc[
        lambda x: x.str.contains('title')
    ].str.extract('title=\"([^\"]*)',expand=False))

df.update(
    df.Neighbourhood.loc[
        lambda x: x.str.contains('Toronto')
    ].str.replace(", Toronto",""))
df.update(
    df.Neighbourhood.loc[
        lambda x: x.str.contains('Toronto')
    ].str.replace("\(Toronto\)",""))


# In[30]:


Toronto = pd.DataFrame({'Postcode':df.Postcode.unique()})
Toronto.shape


# In[31]:


Toronto['Borough']=pd.DataFrame(list(set(df['Borough'].loc[df['Postcode'] == x['Postcode']])) for i, x in Toronto.iterrows())
Toronto['Neighbourhood']=pd.Series(list(set(df['Neighbourhood'].loc[df['Postcode'] == x['Postcode']])) for i, x in Toronto.iterrows())
Toronto['Neighbourhood']=Toronto['Neighbourhood'].apply(lambda x: ', '.join(x))
Toronto.dtypes

Toronto.head()


# In[32]:


table_columns=['Postalcode', 'Borough', 'Neighbourhood']
toronto = pd.DataFrame(columns = table_columns)
content = soup.find('div', class_='mw-parser-output')
table= content.table.tbody
postcode=0
borough=0
neighborhood=0

for tr in table.find_all('tr'):
    i=0
    for td in tr.find_all('td'):
        if i == 0:
            postcode = td.text
            i= i+1
        elif i==1:
            borough = td.text
            i=i+1
        elif i==2:
            neighbourhood = td.text.strip('\n').replace(']','')
        toronto = toronto.append({'Postalcode': postcode, 'Borough': borough, 'Neighbourhood':neighbourhood}, ignore_index=True)

toronto = toronto[toronto.Borough!='Not assigned']
toronto = toronto[toronto.Borough!=0]
toronto.reset_index(drop=True, inplace=True)
i=0
for i in range(0,toronto.shape[0]):
    if toronto.iloc[i][2] == 'Not assigned':
        toronto.iloc[i][2]= toronto.iloc[i][1]
        i=i+1
df= toronto.groupby(['Postalcode','Borough'])['Neighbourhood'].apply(', '.join).reset_index()
df.head(12)


# In[23]:


toronto.shape


# In[24]:


toronto


# In[ ]:




