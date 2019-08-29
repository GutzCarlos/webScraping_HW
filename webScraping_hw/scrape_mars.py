# Dependencies
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import pymongo
import os
import pandas as pd

#os.chdir("C:/Users/gutie/Dropbox/Documentos Insumos/PREWORK_CGF/GitLab/TECMC201905DATA2/Week 12 - Web-Scraping-and-Document-Databases/Homework/Homework")

def scrape_info():
    
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    
    url="https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    News=soup.find('li', class_='slide')
    news_title=News.find('div', class_="content_title").text
    news_p = News.find('div', class_="article_teaser_body").text
    
    url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    Images=soup.find('li', class_='slide')
    featured_image_url="https://www.jpl.nasa.gov"+Images.find('a')['data-fancybox-href']
    
    url="https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    Tweet=soup.find('li', class_='js-stream-item stream-item stream-item')
    mars_weather=Tweet.find('div', class_="js-tweet-text-container").text
    
    url="https://space-facts.com/mars/"
    tables = pd.read_html(url)
    Tabla=tables[0].to_html(index=False)
    Tabla=Tabla.replace("\n","")
    
    url="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    Hem=soup.find_all('div', class_='item')
    #hemisphere_image_urls = {'title': [], 'img_url': []}
    hemisphere_image_urls = []
    
    for hem in Hem:
        url_n="https://astrogeology.usgs.gov"+hem.find('a')['href']
        browser.visit(url_n)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        hemisphere_image_urls.append({'title':soup.find('h2').text.replace(" Enhanced",""), 'img_url':soup.find_all('li')[0].find('a')['href']})

    browser.quit()
    
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.Mission2Mars
    collection0 = db.Hemispheres
    collection1 = db.Facts
    collection2 = db.Weather
    collection3 = db.Image
    collection4 = db.News
    collection = db.M2M
    
    collection0.insert_many(hemisphere_image_urls, ordered=False)
    collection1.insert_one({'facts':Tabla})
    collection2.insert_one({'weather':mars_weather})
    collection3.insert_one({'image':featured_image_url})
    collection4.insert_one({'LN_tile':news_title, 'LN_text':news_p})
    collection.insert_one({'LN':{'LN_title':news_title, 'LN_text':news_p},
                            'weather':mars_weather,
                            'image':featured_image_url,
                            'facts':Tabla,
                            'hemispheres':hemisphere_image_urls})