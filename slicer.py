import math
def staic_per_month(collection):
    time_slice_collection = {}
    for page in collection:
        dt = page[0]
        month = dt[0:6] #slice per month
        if not(month in time_slice_collection):
            time_slice_collection[month] = []
        time_slice_collection[month].append(page)
    #for t in time_slice_collection.keys():
    #    print t, len(time_slice_collection[t])
    return time_slice_collection

def dynamic_per_number_of_mementos(collection, n):
    dynamic_slice_collection = {}
    count = 0
    slice_id = 1
    dynamic_slice_collection[slice_id] = []
    for page in collection:
        print page
        if count == n:
            slice_id = slice_id + 1
            dynamic_slice_collection[slice_id] = []
            count = 0
        dynamic_slice_collection[slice_id].append(page)
        count = count + 1
     
    print "Slice\tSize"
    for t in dynamic_slice_collection.keys():
           print str(t)+"\t"+str( len(dynamic_slice_collection[t]))
    return dynamic_slice_collection

def static_per_slice_number(collection):
    number_of_slices = 28 + math.log(len(collection))
    mementos_per_slice_count = math.ceil(len(collection)/number_of_slices)
    print mementos_per_slice_count
    static_slice_collection = dynamic_per_number_of_mementos(collection, mementos_per_slice_count)
    return static_slice_collection