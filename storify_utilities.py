import json
import requests
from newspaper import Article
from urlparse import urlparse
import time
from rake import Rake
import os
import codecs
import requests
def get_status_code(uri):
    try:
        r = requests.head(uri, allow_redirects=True)
        return r.status_code
    except requests.ConnectionError:
        return 500
    except requests.exceptions.InvalidSchema:
        return 500

def submit_article_to_storify(all_selected_pages, api_key , base_dir, title="Storify test", slug="stories"):
    post_header={}
     #enter the api key 
    api_key="" 
     #enter the username
    post_header['username']=''
    post_header['api_key']=api_key
    post_header['_token']=get_token(api_key)
    post_header['publish']=True

    story = {}
    story["title"]= title
  #  story["description"]= "This is an automatically generated story from Archive-It collection."
    story["slug"]= slug+"a"
    story['elements'] = []
    story_dict = {}
    for page in all_selected_pages:
        memento_uri=page[1].replace('http://archiveit.prod.odu.edu:8080/','http://wayback.archive-it.org/')
        link = {}
        link['type'] = "link"
        link['permalink'] = memento_uri
        if len(page) < 4:
            print page
            continue
        article = get_article_info(memento_uri, page[0], page[3], base_dir)
        data = {}
        dt = None #article.publish_date
        t = time.strptime(page[0][0:8], "%Y%m%d")
        dt_key = None
        if dt != None:
            data['title'] = dt.strftime('%Y-%m-%d')+" - "+ article.title
            dt_key = dt.strftime('%Y%m%d')
        else:
            data['title'] = time.strftime('%Y-%m-%d',t)+ " - "+article.title
            dt_key = time.strftime('%Y%m%d', t)
        keyword = "" #"<strong>"+get_keyword(article.text).title()+"</strong></br>"
        
        if len(article.summary)>300:
            data['description'] = keyword+article.summary[0:300]+"..."
        else:
            data['description'] = article.summary
        data['thumbnail'] = article.top_image
        '''            
        if article.top_image != None and article.top_image != "":
           if get_status_code(article.top_image) < 400:
             data['thumbnail'] = article.top_image #rewrite_image_url(memento_uri, article.top_image)
           elif not(article.top_image.startswith('http://wayback.') ):
             new_written_image = rewrite_image_url(memento_uri, article.top_image)
             print "Origin al image: " + article.top_image
             print "Rewritten image: " + new_written_image
             if get_status_code(new_written_image) < 400:
               data['thumbnail'] = new_written_image 
        '''               
        domain_name = get_domain_name(memento_uri)
        #print domain_name
        link['data'] = {"link":data}
        link['attribution']={"name":domain_name,"href":"http://"+domain_name}
        link['source']={"name":domain_name,"href":"http://"+domain_name}
        #story['elements'].append(link)
        if dt_key not in story_dict:
            story_dict[dt_key] = []
        story_dict[dt_key].append(link)
    for key in sorted(story_dict):
        for l in story_dict[key]:
            story['elements'].append(l)

        
    post_header['story'] = json.dumps(story)
    print post_header
    url = 'https://api.storify.com/v1/stories/mturk_exp/create'
    r = requests.post(url, data=post_header)
def rewrite_image_url(memento_uri, image_url):
    if image_url == "":
        return ""
    
    base_ait_idx_http_end = memento_uri.find('http:',10)
    base_ait_idx_https_end = memento_uri.find('https:',10)
    base_ait_idx_end = max(base_ait_idx_http_end,base_ait_idx_https_end)
    base_ait_url = memento_uri[ 0: base_ait_idx_end].replace('id_/','/')
    memento_base_host = memento_uri[base_ait_idx_end: memento_uri.find('/',base_ait_idx_end+7)]
    image_rel = image_url.replace(base_ait_url,'')
    image_rel = image_rel.replace('http://wayback.archive-it.org/','')
    if image_rel.startswith('http://') or image_rel.startswith('https://'):
        return base_ait_url[0:-1]+"im_/"+image_rel

    return base_ait_url[0:-1]+"im_/"+memento_base_host+"/"+image_rel
   
def get_keyword(text):
    rake = Rake("SmartStoplist.txt")
    if text == "":
        return ""
    keywords = rake.run(text)
    return keywords[0][0]

def get_domain_name(memento_uri):
    org_url_idx = memento_uri.find('http',10)
    if(org_url_idx == -1):
        return "archive-it.org"
    org_url = memento_uri[org_url_idx:]
    return urlparse(org_url).hostname

def get_token(api_key):  
    return '42d757db700c12dcb540eb2da21a65fa'
    post_header={}
    post_header['api_key']=api_key
    post_header['username']='mturk_exp'
    post_header['password']='classes11'
    url = 'https://api.storify.com/v1/auth'
    r = requests.post('https://api.storify.com/v1/auth', data=post_header)
    return str(json.loads(r.content)['content']['_token'])

def get_article_info(memento_url, dt, uri_id, base_dir):
    print memento_url    
    article = Article(memento_url)
    html = get_uri_offline_data(dt, uri_id, "html", base_dir)
    article.download(html)
    article.parse()
    text = get_uri_offline_data(dt, uri_id, "txt", base_dir)
    if text != None:
        article.text = text
    article.nlp()
    return article

def get_uri_offline_data(dt, uri_id, ext, base_dir):
    return None
    if ext == "txt":
        data_base_dir = base_dir + "/text/"
    else:
        data_base_dir = base_dir + "/html/"
    
    file_path = data_base_dir + uri_id+"/"+dt+"."+ext
    if os.path.exists(file_path):        
        text = codecs.open(file_path, encoding='utf-8', mode='r').read()
        if len(text)>0:
            return text
    return None
def get_domain_name(memento_uri):
    org_url_idx = memento_uri.find('http',10)
    if(org_url_idx == -1):
        return "archive-it.org"
    org_url = memento_uri[org_url_idx:]
    return urlparse(org_url).hostname


def prepare_link_to_storify(memento_uri, memento_dt):
     link = {}
     link['type'] = "link"
     link['permalink'] = memento_uri
     print memento_uri     
     domain_name = get_domain_name(memento_uri)
     t = time.strptime(memento_dt[0:8], "%Y%m%d")
     link['attribution']={"name":domain_name+"  @ "+time.strftime('%d, %b %Y',t),"href":"http://"+domain_name}
     link['source']={"name":domain_name+" @ "+time.strftime('%d, %b %Y',t),"href":"http://"+domain_name}       
     return link

def submit_link_to_storify(all_selected_pages, api_key , base_dir, title="Storify test", slug="stories"):
     post_header={}
     #enter the api key 
     api_key="" 
     #enter the username
     
     post_header['username']=''
     account_name = ""
     
     post_header['api_key']=api_key
     post_header['_token']=get_token(api_key)
     post_header['publish']=True
     story = {}
     story["title"]= title
  #   story["description"]= "This is an automatically generated story from Archive-It collection."
     story["slug"]= slug+"s" #"auto-stories-from-archived-collections"
     story['elements'] = []
#     
     for page in all_selected_pages:
         story['elements'].append(prepare_link_to_storify(page[1].replace('http://archiveit.prod.odu.edu:8080/','http://wayback.archive-it.org/'),page[0]))
     post_header['story'] = json.dumps(story)
     print post_header
     url = 'https://api.storify.com/v1/stories/'+account_name+'/create'
     r = requests.post(url, data=post_header)
     
  