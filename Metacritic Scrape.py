#!/usr/bin/env python
# coding: utf-8

# ## Web Scraping from Metacritic
# 
# ### Introduction 

# In[1]:


#Import Packages
import re
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen
from langdetect import detect


# ### Scraping User Reviews for Both Movies

# In[2]:


#Building list of URLs of user reviews for Endgame
base1 = 'https://www.metacritic.com/movie/avengers-endgame/user-reviews?page='
endgame_urls = [(f'{base1}{i}') for i in range(12)]
endgame_urls


# In[3]:


#Building list of URLs of user reviews for Infinity War
base2 = 'https://www.metacritic.com/movie/avengers-infinity-war/user-reviews?page='
infinity_urls = [(f'{base2}{i}') for i in range(9)]
infinity_urls


# In[4]:


#Function to scrape user reviews & data from URLs into Pandas df 

def scrape_user_reviews(urls):
    
    #Empty Lists to hold data
    user, review, date, user_score, review_votes, review_upvotes, review_downvotes = ([] for i in range(7))
    
    for url in urls: 
        req_headers = {}
        req_headers['user-agent'] = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'

        # Creating a request object
        req = Request(url, headers=req_headers)

        # Requesting data from the website & creating BeautifulSoup Object
        try:
            response = urlopen(req)
            page_content = response.read()
            bs = BeautifulSoup(page_content, 'lxml')
        except Exception as e:
            print(e)
            
        #Scraping reviews from review_body tag
        a = bs.find_all('div', class_="review_body")

        #Bunch of string cleaning, removing additional HTML tags, etc
        reviews = [str(i).replace('\n', ' ') for i in a]
        reviews = [re.sub("<span class=\"blurb blurb_collapsed\">.*?span>", "", i) for i in reviews]
        reviews = [re.sub('<.*?>', '', i) for i in reviews]
        reviews = [i.replace('This review contains spoilers, click expand to view.', '').replace('… Expand', '').strip()
                   for i in reviews]
        for i in reviews:
            review.append(i)
            
        #Scraping review author i.e. username
        b = bs.find_all(class_="author")
        users = [re.sub('<.*?>', '', str(i)) for i in b]
        for i in users: 
            user.append(i)
            
        #Scraping date review was wrriten
        c = bs.find_all(class_="date")
        dates = [re.sub('<.*?>', '', str(i)) for i in c]
        for i in dates:
            date.append(i)
            
        #Scraping score given by reviewer
        d = bs.find_all(class_="metascore_w")
        d = [str(i) for i in d]
        scores = []
        for i in d: 
            if 'indiv' in i:
                clean_i = re.sub('<.*?>', '', i)
                scores.append(int(clean_i))      
        for i in scores:
            user_score.append(i)
        
        #Scraping total votes the review received
        e = bs.find_all(class_="total_count")
        total_votes = [re.sub('<.*?>', '', str(i)) for i in e]
        total_votes = [int(i) for i in total_votes]
        for i in total_votes:
            review_votes.append(i)
        
        #Scraping upvotes the review received
        f = bs.find_all(class_="yes_count")
        upvotes = [re.sub('<.*?>', '', str(i)) for i in f]
        upvotes = [int(i) for i in upvotes]
        for i in upvotes:
            review_upvotes.append(i)

        #Calculating the number of downvotes the review received 
        downvotes = [i1-i2 for i1, i2 in zip(total_votes, upvotes)]
        for i in downvotes:
            review_downvotes.append(i)
            
    #Creating dataframe with lists
    reviews_df = pd.DataFrame({'user':user, 'review':review, 'date':date, 'user_score':user_score, 
                               'review_votes':review_votes, 'review_upvotes':review_upvotes, 
                               'review_downvotes':review_downvotes})
    return reviews_df
            


# In[5]:


endgame_reviews = scrape_user_reviews(endgame_urls)
# Convert date column to datetime
endgame_reviews['date'] = pd.to_datetime(endgame_reviews['date'])
endgame_reviews.head(25)


# In[6]:


infinity_reviews = scrape_user_reviews(infinity_urls)
# Convert date column to datetime
infinity_reviews['date'] = pd.to_datetime(infinity_reviews['date'])
infinity_reviews.head(25)


# ### Scraping Critic Reviews for Both Movies 

# In[7]:


endgame_critics = 'https://www.metacritic.com/movie/avengers-endgame/critic-reviews'
infinity_critics = 'https://www.metacritic.com/movie/avengers-infinity-war/critic-reviews'


# In[8]:


def scrape_critic_reviews(url):
        
    req_headers = {}
    req_headers['user-agent'] = r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'

    # Creating a request object
    req = Request(url, headers=req_headers)

    # Requesting data from the website
    try:
        response = urlopen(req)
        page_content = response.read()
        bs = BeautifulSoup(page_content, 'lxml')
    except Exception as e:
        print(e)
        
    #Scraping critic review (not full review - snipet posted on Metacritic)
    a = bs.find_all(class_="no_hover")
    a = [str(i).replace('\n', '') for i in a]
    reviews = [re.sub('<.*?>', '', i).strip() for i in a]

    #Scraping external link for each review
    links = []
    for i in a:
        x = re.search(r'\"http.*?\"', i).group(0).replace('"', '')
        links.append(x)
    
    #Scraping each review's critic/author
    b = bs.find_all(class_="author")
    authors = [re.sub('<.*?>', '', str(i)) for i in b]
    
    #Scraping each review's date
    c = bs.find_all(class_="date")
    dates = [re.sub('<.*?>', '', str(i)) for i in c]
    
    #Scraping each review's score given by critic
    d = bs.find_all(class_="metascore_w")
    d = [str(i) for i in d]
    scores = []
    for i in d: 
        if 'indiv' in i:
            clean_i = re.sub('<.*?>', '', i)
            scores.append(int(clean_i))
    
    #Scraping the publication the review was posted at
    e = bs.find_all(class_="title pad_btm_half")
    e = [str(i) for i in e]
    sites = []
    for i in e:
        x = re.search(r'/publication.*?\?', i).group(0).replace('/publication/', '').replace('?', '').replace('-',' ')
        sites.append(x)
    
    #Creating dataframe with lists
    critics_df = pd.DataFrame({'author':authors, 'review':reviews, 'date':dates, 'critic_score':scores, 
                               'publication':sites, 'review_link':links})
    return critics_df          
    


# In[9]:


endgame_critic_reviews = scrape_critic_reviews(endgame_critics)
# Convert date column to datetime
endgame_critic_reviews['date'] = pd.to_datetime(endgame_critic_reviews['date'])
endgame_critic_reviews.head(25)


# In[10]:


infinity_critic_reviews = scrape_critic_reviews(infinity_critics)
# Convert date column to datetime
infinity_critic_reviews['date'] = pd.to_datetime(infinity_critic_reviews['date'])
infinity_critic_reviews.head(25)


# ### Pairing down reviews by date

# In[11]:


#Infinity War Release & DVD Dates

inf_release = datetime(2018, 4, 23)
inf_release_1 = inf_release + timedelta(days=60)

inf_dvd = datetime(2018, 7, 31)
inf_dvd_1 = inf_dvd + timedelta(days=60)


# In[12]:


#Endgame Release & DVD Dates

end_release = datetime(2019, 4, 26)
end_release_1 = end_release + timedelta(days=60)

end_dvd = datetime(2019, 7, 30)
end_dvd_1 = end_dvd + timedelta(days=60)


# In[13]:


inf_filtered = infinity_reviews[(infinity_reviews['date'] >= inf_release) & (infinity_reviews['date'] <= inf_dvd_1)]
inf_filtered = inf_filtered[(inf_filtered['date'] <= inf_release_1) | (inf_filtered['date'] >= inf_dvd)]

inf_filtered


# In[14]:


end_filtered = endgame_reviews[(endgame_reviews['date'] >= end_release) & (endgame_reviews['date'] <= end_dvd_1)]
end_filtered = end_filtered[(end_filtered['date'] <= end_release_1) | (end_filtered['date'] >= end_dvd)]

end_filtered


# ### Removing non-English reviews

# In[15]:


#Inifity War reviews; testing language and filtering out non-English reviews with langdetect

filt_reviews = list(inf_filtered['review'])
language = []
for i in filt_reviews: 
    try:
        if detect(i) == 'en':
            language.append('English')
        else:
            language.append('Non-English')
    except:
        language.append('Non-English')

inf_filtered['language'] = language
inf_filtered = inf_filtered[inf_filtered['language']=='English']


# In[16]:


#Endgame reviews; testing language and filtering out non-English reviews with langdetect

filt_reviews = list(end_filtered['review'])
language = []
for i in filt_reviews: 
    try:
        if detect(i) == 'en':
            language.append('English')
        else:
            language.append('Non-English')
    except:
        language.append('Non-English')

end_filtered['language'] = language
end_filtered = end_filtered[end_filtered['language']=='English']


# In[17]:


#Uncomment and run to save dfs as CSVs

# inf_filtered.to_csv('infinity_reviews.csv')
# end_filtered.to_csv('endgame_reviews.csv')

# infinity_critic_reviews.to_csv('infinity_critics.csv')
# endgame_critic_reviews.to_csv('endgame_critics.csv')


# In[ ]:




