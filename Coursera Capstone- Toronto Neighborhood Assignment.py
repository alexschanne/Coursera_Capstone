#!/usr/bin/env python
# coding: utf-8

# <H1> Coursera Capstone- Toronto Neighbourhood Assignment

# This notebook is in response to Coursera Capstone Week 3 assignment. It will utilize Foursquare API and newly acquired skills from the course.

# In[1]:


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


# <H1> Scraping Website

# Now that the libraries are imported, we can begin scraping the website.

# In[2]:


#linking and scraping website
r= requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M')
soup = BeautifulSoup(r.text, 'html.parser')
table= soup.find('table', attrs={'class':'wikitable sortable'})

headers=table.findAll('th')
for i, head in enumerate(headers): headers[i]=str(headers[i]).replace("<th>","").replace("</th>","").replace("\n","")

rows=table.findAll('tr')
rows=rows[1:len(rows)]

for i, row in enumerate(rows): rows[i] = str(rows[i]).replace("\n</td></tr>","").replace("<tr>\n<td>","")
for i, row in enumerate(rows): rows[i] = str(rows[i]).replace("<https://>", "")

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

Toronto = pd.DataFrame({'Postcode':df.Postcode.unique()})
Toronto['Borough']=pd.DataFrame(list(set(df['Borough'].loc[df['Postcode'] == x['Postcode']])) for i, x in Toronto.iterrows())
Toronto['Neighbourhood']=pd.Series(list(set(df['Neighbourhood'].loc[df['Postcode'] == x['Postcode']])) for i, x in Toronto.iterrows())
Toronto['Neighbourhood']=Toronto['Neighbourhood'].apply(lambda x: ', '.join(x))
Toronto.dtypes

Toronto.head()


# In[3]:


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
            neighborhood = td.text.strip('\n').replace(']','')
        toronto = toronto.append({'Postalcode': postcode, 'Borough': borough, 'Neighbourhood':neighborhood}, ignore_index=True)

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


# In[4]:


dfll= pd.read_csv("http://cocl.us/Geospatial_data")
dfll.rename(columns={'Postal Code':'Postcode'}, inplace=True)
dfll.set_index("Postcode")
Toronto.set_index("Postcode")
toronto_data=pd.merge(Toronto, dfll)
toronto_data.head(12)


# In[5]:


address = 'Toronto, ON, Canada'

geolocator = Nominatim(user_agent="Jupyter")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto, ON, Canada are {}, {}.'.format(latitude, longitude))


# In[6]:


map_toronto=folium.Map(location=[latitude, longitude], zoom_start=10)
map_toronto


# In[7]:


from IPython.display import HTML, display
map_toronto=folium.Map(location=[latitude, longitude])
for lat, lng, borough, neighbourhood in zip(toronto_data['Latitude'], toronto_data['Longitude'], toronto_data['Borough'], toronto_data['Neighbourhood']):
    label= '{}, {}'.format(neighbourhood, borough)
    label=folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)
        
map_toronto


# In[8]:


#Foursquare Credentials

CLIENT_ID = 'GCLKXCIUP2HPNJKHP03BLDMFU2VHZDDMIHZP4RIPJJSNAYGB'
CLIENT_SECRET = 'GHSMJAUI1YLPIBHENISF5HI2IFVOC0OS5L1UM4OA2TO3OZJB'
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[9]:


toronto_data.loc[0, 'Neighbourhood']


# In[10]:



neighbourhood_latitude = toronto_data.loc[0, 'Latitude']  
neighbourhood_longitude = toronto_data.loc[0, 'Longitude'] 
neighbourhood_name = toronto_data.loc[0, 'Neighbourhood'] 

print('Latitude and longitude values of {} are {}, {}.'.format(neighbourhood_name, 
                                                               neighbourhood_latitude, 
                                                               neighbourhood_longitude))


# In[11]:


#Get URL
LIMIT = 100
radius = 500
url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighbourhood_latitude, 
    neighbourhood_longitude, 
    radius, 
    LIMIT)
url 


# In[12]:


results = requests.get(url).json()
results


# In[13]:


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[14]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[15]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# <H2>Foursquare: Neighborhoods in Toronto

# In[16]:


#Repeating the process for the other neighborhoods
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighbourhood', 
                  'Neighbourhood Latitude', 
                  'Neighbourhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[17]:


toronto_venues = getNearbyVenues(names=toronto_data['Neighbourhood'],
                                   latitudes=toronto_data['Latitude'],
                                   longitudes=toronto_data['Longitude']
                                  )


# In[18]:


print(toronto_venues.shape)
toronto_venues.head()


# In[19]:


toronto_venues.groupby('Neighbourhood').count()


# In[20]:


print('There are {} uniques categories.'.format(len(toronto_venues['Venue Category'].unique())))


# <H2> Analysing Neighbourhoods

# In[21]:


toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")

toronto_onehot['Neighbourhood'] = toronto_venues['Neighbourhood'] 

fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1])
toronto_onehot = toronto_onehot[fixed_columns]

toronto_onehot.head()


# In[22]:


toronto_onehot.shape


# In[23]:


toronto_grouped = toronto_onehot.groupby('Neighbourhood').mean().reset_index()
toronto_grouped


# In[24]:


toronto_grouped.shape


# In[25]:


num_top_venues = 5

for hood in toronto_grouped['Neighbourhood']:
    print("----"+hood+"----")
    temp = toronto_grouped[toronto_grouped['Neighbourhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# In[26]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[27]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

columns = ['Neighbourhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

neighbourhoods_venues_sorted = pd.DataFrame(columns=columns)
neighbourhoods_venues_sorted['Neighbourhood'] = toronto_grouped['Neighbourhood']

for ind in np.arange(toronto_grouped.shape[0]):
    neighbourhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)

neighbourhoods_venues_sorted.head()


# <H2>5 Clusters of Neighborhoods

# In[28]:


#KMeans Clustering
kclusters = 5

toronto_grouped_clustering = toronto_grouped.drop('Neighbourhood', 1)

kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering)

kmeans.labels_[0:10]


# In[29]:


#labeling clusters
neighbourhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

toronto_merged = toronto_data

toronto_merged = toronto_merged.join(neighbourhoods_venues_sorted.set_index('Neighbourhood'), on='Neighbourhood')

toronto_merged.head()


# In[30]:



map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

markers_colors = []
for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'], toronto_merged['Neighbourhood'], toronto_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        fill=True,
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[31]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 0, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[32]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 1, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[33]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 2, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[34]:


toronto_merged.loc[toronto_merged['Cluster Labels'] == 3, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[35]:



toronto_merged.loc[toronto_merged['Cluster Labels'] == 4, toronto_merged.columns[[1] + list(range(5, toronto_merged.shape[1]))]]


# In[ ]:





# In[ ]:




