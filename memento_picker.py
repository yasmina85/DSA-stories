from urlparse import urlparse
import re
import os

def get_memento_depth(mem_uri):
    if mem_uri.endswith('/'):
        mem_uri = mem_uri[0:-1]
    original_uri_idx = mem_uri.find('http',10)
    original_uri = mem_uri[original_uri_idx+7:-1]
    level = original_uri.count('/')
    return level/10.0

def get_memento_uri_category(memento_uri):
    base_ait_idx_end = memento_uri.find('http',10)
    original_uri = memento_uri[ base_ait_idx_end:]
    
    o = urlparse(original_uri)
    hostname = o.hostname
    if hostname == None:
        return -1  
    if  bool(re.search('.*twitter.*', hostname)) or bool(re.search('.*t.co.*', hostname)) or \
        bool(re.search('.*redd.it.*', hostname)) or bool(re.search('.*twitter.*', hostname)) or \
        bool(re.search('.*facebook.*', hostname)) or bool(re.search('.*fb.me.*', hostname)) or \
        bool(re.search('.*plus.google.*', hostname))  or   bool(re.search('.*wiki.*', hostname)) or \
        bool(re.search('.*globalvoicesonline.*', hostname))  or  bool(re.search('.*fbcdn.*', hostname)):
        return 0.5
    elif  bool(re.search('.*cnn.*', hostname)) or  bool(re.search('.*bbc.*', hostname)) or \
        bool(re.search('news', hostname)) or  bool(re.search('.*news.*', hostname)) or  \
        bool(re.search('.*rosaonline.*', hostname))or  bool(re.search('.*aljazeera.*', hostname)) or  \
        bool(re.search('.*guardian.*', hostname)) or  bool(re.search('.*USATODAY.*', hostname)) or  \
        bool(re.search('.*nytimes.*', hostname))or  bool(re.search('.*abc.*', hostname))or  \
        bool(re.search('.*foxnews.*', hostname)) or  bool(re.search('.*allvoices.*', hostname)) or \
        bool(re.search('.*huffingtonpost.*', hostname)) :
        return 0.7 
    elif  bool(re.search('.*dailymotion.*', hostname)) or  \
        bool(re.search('.*youtube.*', hostname)) or \
        bool(re.search('.*youtu.be.*', hostname)): 
        return 0.7
    elif bool(re.search('.*wordpress.*', hostname)) or  bool(re.search('.*blog.*', hostname)):
        return 0.4
    elif  bool(re.search('.*flickr.*', hostname)) or bool(re.search('.*flic.kr.*', hostname)) or  \
        bool(re.search('.*instagram.*', hostname)) or  bool(re.search('.*twitpic.*', hostname)):
        return 0.6
    else:
        return 0

def choose_best_memento(pages):
    print "\nNew cluster of size "+str(len(pages))+"\nMembers are:"
    #Customize the weights 
    damage_wt = -0.40 # THIS IS NEGATIVE VALUE
    category_wt = 0.15
    level_wt = 0.45
    score_dict = {}
    for idx, page in enumerate(pages):
        memento_uri = page[1].replace('http://archiveit.prod.odu.edu:8080/','http://wayback.archive-it.org/')
      #  print page
        damage_val = float(page[3]) #get_memento_damage(memento_uri)

        if damage_val == None:
            damage_val = 0
        category_val = get_memento_uri_category(memento_uri)
        level_val = get_memento_depth(memento_uri)
        score = damage_wt * damage_val + category_wt * category_val + level_wt * level_val
        score_dict[idx] = score
        print idx, memento_uri
        print damage_val, category_val, level_val, score

    best_memento_idx = -1
    score_value = -100
    for memento_idx in score_dict.keys():
        if score_dict[memento_idx] > score_value:
            score_value = score_dict[memento_idx]
            best_memento_idx = memento_idx
    print "Best Memento is: " +str(best_memento_idx) + "\tScore: "+str(score_value)
    return best_memento_idx
        
     