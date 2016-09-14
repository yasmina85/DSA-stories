import os

def get_memento_damage(mem_uri):
    print mem_uri
    quality_results_stream = os.popen('perl damage_ijdl/measureMemento.pl '+mem_uri)
    quality_results = quality_results_stream.read()
    
    fields = quality_results.split('\n')
    pct = None
    total = None
    for field in fields:
        if(field.startswith('TOTAL')):
            total = float(field[6:])
        elif(field.startswith('PCT_MISSING')):
            pct = float(field[12:])
    return total


def compute_quality_damage(collection_directory):
    timemap_file_englith = open(collection_directory+"/timemap_english.txt")
    timemap_file_quality_path = collection_directory+"/timemap_quality.txt"
    
    if  os.path.exists(timemap_file_quality_path):
        print "Using cached tmiemap quality file at " + timemap_file_quality_path
        return
    timemap_file_quality_path = open(timemap_file_quality_path,'w')
    #2	20131001204132	http://wayback.archive-it.org/3936/20131001204132/http://archives.gov/

    number_of_mementos = 0
    for memento_record in timemap_file_englith:
        fields = memento_record.split("\t")
        uri_id = fields[0]
        dt = fields[1]
        uri = fields[2].replace("\n","")
        #print uri
        memento_damage = get_memento_damage(uri)
        if memento_damage == None:
            print "Error in getting quality for "+uri 
            memento_damage = 0     
        #print memento_damage
        #print ""
        
        timemap_file_quality_path.write(uri_id + "\t" + dt + "\t" + uri + "\t" + str(memento_damage) + "\n")
    timemap_file_quality_path.close()
        
    
         
    