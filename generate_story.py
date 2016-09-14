import re
import sys
import os
sys.path.append("source_code")
import seed_extractor
import timemap_downloader
import argparse
import random
import html_wayback_downloader
import off_topic_detector_cos_sim
import off_topic_detector_count_words
import urlparse
import story_extractor
import memento_quality_utilities
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

parser = argparse.ArgumentParser(description='Generate Stories.')

parser.add_argument('-d', dest='dir', 
                   help='The directory that is used for the downloaded/processed data')
                   
parser.add_argument('-th', dest='threshold', 
                   help='The threshold to compute the off-topic pages between 0 to 1 for the cosin and from -1 to 1 for the wcount. The default threshold is 0.15')
                
parser.add_argument('-o', dest='file', 
                   help='The file path to write the output')

parser.add_argument('-t', dest='timemap_uri', 
                   help='The link of a timemap (it should be in timemap/link format)')
#http://wayback.archive-it.org/694/timemap/link/http
parser.add_argument('-i', dest='id', 
                   help='The collection id as appeared on archive-it')

parser.add_argument('-r', dest='uri', 
                   help='The collection uri as appeared on archive-it')

parser.add_argument('-m', dest='mode', default="cosin",
                   help='The similarity measure: cosin or wcount. The default is cosin.')

parser.add_argument('-title', dest='title', default="Automated Story",
                   help='The title of the generated story.')

parser.add_argument('-s', dest='selection', default="random",
                   help='Selecting the memento from a cluster.')

parser.add_argument('-st', dest='starttime', default="19900101120101",
                   help='Start time, default 19900101120101.')
                   
parser.add_argument('-et', dest='endtime', default="20161231120101",
                    help='End time, default 20161231120101.')
parser.add_argument('-l', dest='slug', default="stories",
                    help='Storify slug')
args = parser.parse_args()

data_directory = '/Users/yasminalnoamany/Documents/PHD_documents/temp_data'
if args.dir != None:
   data_directory =  args.dir
   
threshold = 0.1
if args.threshold != None:
   threshold =  float(args.threshold)

output_file = sys.stdout
if args.file != None:
    output_file = open(args.file,'w')

if args.mode != None:
    mode = args.mode 
    
    if mode != "cosin" and mode != "wcount":
         parser.print_help()
         sys.exit(1)
         
base_timemap_link_uri = "https://wayback.archive-it.org/"
if args.id !=None:
    # extract from id
    collection_id = args.id
    collection_directory = data_directory+"/collection_"+str(collection_id)
    seed_extractor.seed_extractor_from_id(collection_id,collection_directory)
    seed_list_file = collection_directory+"/seed_list.txt"
    timemap_file_name = collection_directory+"/timemap.txt"
    timemap_downloader.download(seed_list_file, base_timemap_link_uri+ str(collection_id)+"/timemap/link", collection_directory, args.starttime, args.endtime)
    
elif args.uri !=None:
    # extract from uri
    collection_uri = args.uri
    o = urlparse.urlparse(args.uri)
    collection_id = o.path.split('/')[-1]
    if collection_id == "":
        collection_id = o.path.split('/')[-2]
        
    collection_directory = data_directory+"/collection_"+str(collection_id)
    seed_list_file = collection_directory+"/seed_list.txt"
    timemap_file_name = collection_directory+"/timemap.txt"
    
    seed_extractor.seed_extractor_from_uri(collection_uri,collection_directory)
    timemap_downloader.download(seed_list_file, base_timemap_link_uri+str(collection_id)+"/timemap/link", collection_directory, args.starttime, args.endtime)
elif args.timemap_uri !=None:
    # extract directly from timemap
    memento_list = timemap_downloader.get_mementos_from_timemap(args.timemap_uri, args.starttime, args.endtime)
    collection_id = str(random.randrange(1000000))
    collection_directory = data_directory+"/collection_"+collection_id
    timemap_file_name =collection_directory+"/timemap.txt"
    ensure_dir(timemap_file_name)
    timemap_file =  open(timemap_file_name,'w')
    timemap_downloader.write_timemap_to_file(1, memento_list,timemap_file) 
else:
    parser.print_help() 

html_wayback_downloader.download_html_from_wayback(timemap_file_name,collection_directory)      
os.system('./extract_text_from_html '+timemap_file_name+' '+  collection_directory)

if not(os.path.exists(collection_directory+"/ontopic_timemap.txt")):
    if mode == "cosin" :
        off_topic_detector_cos_sim.get_off_topic_memento(timemap_file_name,output_file,collection_directory,threshold)
    elif mode ==  "wcount":
        off_topic_detector_count_words.get_off_topic_memento(timemap_file_name,output_file,collection_directory,threshold)
else:
    print "Using cached version of on-topic: "+collection_directory+"/ontopic_timemap.txt"

if not(os.path.exists(collection_directory+"/timemap_english.txt")):
    os.system('./exclude_non_english '+collection_directory+"/ontopic_timemap.txt"+' '+  collection_directory)
else:
    print "Using cached version of english: "+collection_directory+"/timemap_english.txt"
    
memento_quality_utilities.compute_quality_damage(collection_directory)
story_extractor.generate_story(collection_directory, args.title, args.selection, args.slug, args.starttime, args.endtime)

