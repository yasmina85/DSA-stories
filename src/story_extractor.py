import re
import sklearn
import os
import sys
import platform
import glob
import random
import numpy as np
import json
import requests

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

import storify_utilities
import simhash_utilities
import memento_quality_utilities
import slicer
import memento_picker

def read_file(text_file):
    shakes = open(text_file, 'r')
    text = shakes.read()
    if len(text)==0:
        return ""
    words = text.decode('utf-8', errors='ignore').split()
    return words
    

def read_collection_text_files(timemap_list_file, input_base_dir, start_dt, end_dt):
    collection = {}
    simhash_list =[]
    for memento_record in timemap_list_file:
		
		fields = memento_record.split("\t")
		
		uri_id = fields[0]
		dt = fields[1]
		damage = fields[3].replace('\n','')
		if dt < start_dt or dt > end_dt:
		    continue

        # you can add any uri that you want to exclude           
		mem_uri = fields[2].replace('\n','').replace('\r','')	
        
		text_file_path = input_base_dir+"/text/"+uri_id+"/"+dt+".txt"
		if os.path.exists(text_file_path):
			words = read_file(text_file_path)
			if len(words) < 70 and\
              not('youtube.com' in mem_uri) and\
              not('twitter.com' in mem_uri):
			       print  mem_uri, text_file_path      
			       continue
			simhash_value = simhash_utilities.compute_simhash(words)

			if simhash_value == 0 or simhash_value in simhash_list:
				#print simhash_value
				continue
			elif not(uri_id in collection):
                            collection[uri_id] = []
			collection[uri_id].append( (dt, mem_uri, simhash_value, damage))
			simhash_list.append(simhash_value)
		else:
		  print text_file_path
    return collection


def cluster_time_slice(time_slice_list, selection):
	simhash_list = []
	
	for item in time_slice_list:
		simhash_list.append(item[2])
	
	X = np.matrix(simhash_list)
	db = DBSCAN(eps=0.3, min_samples=2, metric=simhash_utilities.myhamdist).fit(X.T)
	clusters = {}
	for index, label in enumerate(db.labels_):
		if not(label in clusters):
			clusters[label] = []
		#print time_slice_list[index]
		clusters[label].append(time_slice_list[index])
	if selection == "quality" :
		return choose_high_quality_memento_from_cluster(clusters)
	else:
		return choose_random_memento_from_cluster(clusters)

def choose_random_memento_from_cluster(clusters):
	selected_pages = []
	for cluster in clusters.keys():
		rindex = random.randrange(len(clusters[cluster]))
		selected_pages.append(clusters[cluster][rindex])
	return selected_pages	

def choose_high_quality_memento_from_cluster(clusters):
    selected_pages = []
    sorted_clusters = sorted(clusters.items(), key=lambda e: len(e[1]), reverse=True)
  #  print clusters.items()
  #  print sorted_clusters
    for idx, cluster in enumerate(sorted_clusters):
   #     print str(idx), str(len(cluster[1]))        
        if idx > 28 and len(cluster[1])<2:
            continue
        rindex = memento_picker.choose_best_memento(cluster[1]) #random.randrange(len(clusters[cluster]))
        selected_pages.append(cluster[1][rindex])
    return selected_pages    
    
def generate_story(base_dir, title, selection, slug, start_dt="19900101121200", end_dt="20200101000000"):
	#reading the collection
	timemap_list_file=open(base_dir+"/timemap_quality.txt")
	collection = read_collection_text_files(timemap_list_file, base_dir, start_dt, end_dt)
	print len(collection)
	reduced_collection = simhash_utilities.remove_near_duplicate(collection)
	print len(reduced_collection)
    
    # Sort by memento datetime
	reduced_collection.sort()
	print reduced_collection
	#Slice collection by number of mementos in each slice
	time_slice_collection = slicer.static_per_slice_number(reduced_collection)

	#cluster the pages of each time slice
	all_selected_pages = []
	for t in time_slice_collection.keys():
		all_selected_pages += cluster_time_slice(time_slice_collection[t], selection)

	#Select random page and then list all the rest of the pages
	all_selected_pages.sort()	
#	for page in all_selected_pages:
#		print page[0],page[1]
	storify_utilities.submit_link_to_storify(all_selected_pages, "", base_dir, title, slug)
	#storify_utilities.submit_article_to_storify(all_selected_pages, "", base_dir, title, slug)

