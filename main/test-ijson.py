import ijson
import json

def reader():
    f = open('gdap_baton_meta.json', 'r')
    objs = ijson.items(f, "")
    #objs = [o['collection'] for o in objs]
    for o in objs:
        for subitem in o:
            for attr, val in list(subitem.items()):
                print("ATTR: " + str(attr) + " VAL = " + str(val) + "\n")
                if attr == 'avus':
                    #avus = json.loads(val)
                    print("AFTER json load: " + str(val))
                    for avu in val:
                        print("A = " + str(avu['attribute']) + " V = " + str(avu['value']) + "\n")

reader()
