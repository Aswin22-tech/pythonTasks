#!/usr/bin/env python
# coding: utf-8

# ### Importing required libraries
# ##### pdfminer is the library used here for parsing pdf file

# In[1003]:


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import json

## Reading the PDF
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


## Parsing the PDF and formatting

def parse_to_json(main_list):
    dic={}
    min_dic={}
    
    # Removing unnecessary characters, newline characters etc.
    main_list = [sub.strip() for sub in main_list]
    main_list = [sub.replace('\n','') for sub in main_list]            
    main_list = [sub.replace('\u200b','') for sub in main_list]

    while("" in main_list) : 
        main_list.remove("")                   
                    
    # Creating a list of sub headings              
    subheadings=['Education','Leadership Experience','Professional Experience','Additional Projects','Skills & Interests']
    length = len(subheadings)
    
    # Setting primary details (Name, Address etc.) directly
    detailing = main_list[:main_list.index(subheadings[0])]
    detailing = [x for x in detailing if "________" not in x]
    dic['Name'] = detailing[0].strip()
    detailing.remove(detailing[0])
    for i,elem in enumerate(detailing):
        if ('|' in elem):
            details = elem.split('|')
            
            for ele in details:
                if(('@' in ele) & ('.com' in ele)):
                    dic['EmailId'] = ele.strip()
                    elem_new = elem.replace(ele,"")
                    elem_new = elem_new.replace('|',"")
                    detailing[i] = elem_new
                    
    dic['Address'] = ','.join(str(ele).strip() for ele in detailing)
    
    # Looping through the sub headings
    for i in range(length):
     
        if(i<length-1):
            
            # All data between current sub heading and next subheading will be inserted to current sub heading
            newlist = main_list[main_list.index(subheadings[i])+1:main_list.index(subheadings[i+1])]
            det =','.join(str(ele).strip() for ele in newlist)
            det = det.replace('\n',"")  
            
            # Horizontal line is removed here
            indices = [i for i, x in enumerate(newlist) if "____________" in x] 
            
            # Horizontal lines cause another issue of flipping data from one subheading to another sub heading,
            # which is handled here
            
            if(len(indices)>1):
      
                edu1 = newlist[indices[0]+1:indices[1]]               
                det1 =','.join(str(ele).strip() for ele in edu1)
                prev_list = main_list[main_list.index(subheadings[i-1])+1:main_list.index(subheadings[i])]
                det2 = ','.join(str(ele).strip() for ele in prev_list)
                
                # Pick the data present in the other sub heading(flipping due to horizontal lines)
                final_det = det2+","+det1
                
                # Attach it back to the right key in the dictionary
                dic[subheadings[i-1]] = final_det
                newlist = [x for x in newlist if x not in newlist[indices[0]:indices[1]]]
                det =','.join(str(ele).strip() for ele in newlist)
                dic[subheadings[i]] = det         
        
            else:                
                newlist = [x for x in newlist if "________" not in x]
                det =','.join(str(ele).strip() for ele in newlist)   
                dic[subheadings[i]] = det
        else:            
            # Adding one more level of granularity in the dictionary       
            newlist = main_list[main_list.index(subheadings[i])+1:]            
            newlist = [x for x in newlist if "________" not in x]
            for elem in newlist:
                key = elem.split(':')[0]
                value = elem.split(':')[1]
                min_dic[key] = value
            dic[subheadings[i]] = min_dic

    return dic


# ### Driver function

# In[ ]:


import sys

if __name__=="__main__":
    print("argument:", sys.argv)
    
    # Picking input file from command line
    inputfile = sys.argv[1]
    print("inputfile:", inputfile)

     # Picking output file from command line
    outputfile = sys.argv[2]
    print("outputfile:", outputfile)    
    
    # Calling the functions
    element = convert_pdf_to_txt(inputfile)

    main_list = element.split('\n')
    diction = parse_to_json(main_list)
    
    # Creating a JSON dump
    with open(outputfile, 'w', encoding ='utf8') as json_file: 
        json.dump(diction, json_file, ensure_ascii = False) 

