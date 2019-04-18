from xlrd import open_workbook
from xlrd import xldate_as_tuple
import xlwt
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import time
import random
import itertools
from scipy.stats import ttest_ind
import subprocess
import csv
import shutil
import collections
import copy
import pandas
from pprint import pprint
import re


#For east africa

config_path = os.path.join("/Users/hsheldah/Dropbox/NorthStar/Havi")
os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi')

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    folder = '/Users/hsheldah/Dropbox/NorthStar/Havi'
else:
    folder = 'D:\\Dropbox\\NorthStar\\Havi'

filename = folder + "/jan17_EA.xlsx"

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/jan17_EA.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = 'D:\\Dropbox\\NorthStar\\Havi\\jan17_EA.xlsx'
    s = wb.sheet_by_index(0)
    
raw_data = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    raw_data.append(row_list)
filename = folder + "RespondentList-20160909.xlsx"
if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/RespondentList-20160909.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = open_workbook('D:\\Dropbox\\NorthStar\\Havi\\RespondentList-20160909.xlsx')
    s = wb.sheet_by_index(0)
respondent_list = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    respondent_list.append(row_list)
respondent_list = respondent_list[1:] # nothing in first row
respondent_list = [row[:4] for row in respondent_list]
respondent_dict = {row[2] : row[1].lower() for row in respondent_list if row[2] != ''}


filename = folder + "Group-emails.xlsx"
if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/Group-emails.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = open_workbook('D:\\Dropbox\\NorthStar\\Havi\\Group-emails.xlsx')
    s = wb.sheet_by_index(0)
group_emails = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    group_emails.append(row_list)
group_emails = group_emails[1:] # nothing in first row
group_emails_dict = {row[2].split('@')[0] : row[1] for row in group_emails if row[2] != ''}


filename = folder + "Missing_names.xlsx"
if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/Missing_names.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = open_workbook('D:\\Dropbox\\NorthStar\\Havi\\Missing_names.xlsx')
    s = wb.sheet_by_index(0)
missing_names = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    missing_names.append(row_list)
missing_dict = {row[0] : row[1] for row in missing_names if row[1] != ''}

names_dict = {key: group_emails_dict[respondent_dict[key]] for key in respondent_dict if respondent_dict[key] in group_emails_dict}

names_dict = {**names_dict, **missing_dict} # combines the dictionaries

resource_categories = ['Financial Support', 'Equipment / supplies', 'Human Resources', 'Information / Expertise', 'Legitimacy / Reputation', 'Advertising / referrals', 'Other']

intra_interaction_categories = ['Socializing / Interpersonal', 'Partnerships', 'Technical (e.g., functioning of COMETs)', 'Healthcare Information','Other (please specify in the comments section below)']

interaction_mode_categories = ['Text (email, SMS, Facebook, WhatsApp...)',
                               'Audio-visual (Telephone, Skype...)',
                               'In person']

## Storing cleaned data into dictionary

# First row is used for reference 
var_names = raw_data[0]
#partner names are stored in the second row. 
partner_names = raw_data[1]


# Rest is raw data
survey_answers = raw_data[2:]

nb_partner_limit = 30 # current number of allowed partners
index_name = var_names.index('Q6')
index_partners = var_names.index('Q3_1_114_East Africa') # finds where the partner names start
index_partners_added = var_names.index('Q3_81_TEXT_East Africa') 
index_nsrate = var_names.index('Q8_1') 
resource_provided_index = var_names.index('Q12_x1_1_East Africa')
resource_provided_added = var_names.index('Q12_x81_TEXT_East Africa')
having_interacted_index = var_names.index('Q14_1')
nb_intra_interaction_index = var_names.index('Q16_x1_3') #number of interactions with people listed
other_int = var_names.index('Q18')
interaction_mode_index = var_names.index('Q20_x1')
other_mode = var_names.index('Q22')
interaction_initiation_index = var_names.index('Q24_x1')
region_index = var_names.index('region')

master_dict = {}
master_dict['people'] = []
def masterdict_2017(survey_answers, partner_names):
    #getting leading and last whitespace out of partner names
    for i in range(len(partner_names)):
        if type(partner_names[i]) == str:
            partner_names[i] = partner_names[i].strip()

    for i in range(len(partner_names)):
        if partner_names[i] == "Susan":
            partner_names[i] = "Susan-Mary Foster"
        if partner_names[i] == "Sylvia Mushumba":
            partner_names[i] = "Sylvia Mushumba-Barure"
    #working with only one row from survey answers at first
    for j in range(len(survey_answers)):
        print(j)
        t =survey_answers[j]
        t2 = t[index_partners:index_partners_added]
        t3 = t[index_partners_added: index_nsrate:2]
        t4 = t[index_partners_added+1: index_nsrate:2]
        t5 = t[resource_provided_index:resource_provided_added]
    #splitting resource list into chunks of 7
        list_res = [t5[i:i + 7] for i in range(0, len(t5), 7)]
        partners = {}
        partners['name'] = []
        partners['nb_interactions'] = []
        partners['res_provided2'] = []
        partners['resources_provided'] = []
   
        for idx, val in enumerate(t2):
            if type(val) == str:
                val = re.sub('[+]', '', val)
                val = float(val)
            value = idx+ index_partners
            if val!=0 and val!= 'NA':
                partners['nb_interactions'].append(val)
                partners['name'].append(partner_names[value])
        for i in range(len(t2)):
            partners['res_provided2'].append(list_res[i])
        
        part_int = partner_names[index_partners: index_partners_added]

        result = [part_int.index(i) for i in partners['name']]
        for i in result:
            partners['resources_provided'].append(partners['res_provided2'][i])
        del(partners['res_provided2'])

#getting into correct format
        
#external partners
        new_dict = {}
        new_dict['name'] = t[index_name]
        new_dict['region'] = t[region_index]
        new_dict['partners'] = []
        for i in range(len(partners['name'])):
            new_dict['partners'].append({})
            new_dict['partners'][i]['name'] = partners['name'][i]
            new_dict['partners'][i]['nb_interactions'] = partners['nb_interactions'][i]
            new_dict['partners'][i]['resources_provided'] = partners['resources_provided'][i]

#resources provided by north star
        nstarrate = t[index_nsrate:resource_provided_index-1]
        new_dict['resources_available'] = nstarrate

#getting internal interactions
        int = t[nb_intra_interaction_index: other_int]
        test = [int[i:i + 5] for i in range(0, len(int), 5)]
        
        tname2 = partner_names[nb_intra_interaction_index: other_int]
        resp_list =tname2[0:len(tname2): 5]
        mode = t[interaction_mode_index: other_mode]
        initiate = t[interaction_initiation_index:]
    
        int1 = t[having_interacted_index]
        internal = int1.split(',')

#turning mode into dummy variable
        for i in range(len(mode)):
            if mode[i] != 0:
                mode[i] = mode[i].split('),')
        
        for i in range(len(mode)):
            if mode[i] != 0:
                if len(mode[i]) == 3:
                    mode[i] = [1,1,1]
                if len(mode[i]) == 0:
                    mode[i] = [0,0,0]
                if mode[i] == ['Text (email, SMS, Facebook, WhatsApp...)']:
                    mode[i] = [1,0,0]
                if mode[i] == ['Text (email, SMS, Facebook, WhatsApp...', 'In person']:
                    mode[i] = [1,0,1]
                if mode[i] == ['In person']:
                    mode[i] = [0,0,1]
                if mode[i] == ['Text (email, SMS, Facebook, WhatsApp...','Audio-visual (Telephone, Skype...)']:
                    mode[i] = [1,1,0]
                if mode[i] == ['Audio-visual (Telephone, Skype...)']:
                    mode[i] = [0,1,0]
                if mode[i] == ['Audio-visual (Telephone, Skype...', 'In person']:
                    mode[i] = [0,1,1]
        
        for i in range(len(mode)):
            if mode[i] == 0:
                mode[i] = [0,0,0]
            
    #getting words out of initiate
        for i in range(len(initiate)):
            if initiate[i] == '7: Strongly agree':
                initiate[i] = '7'
            if initiate[i] == '1: Strongly disagree':
                initiate[i] = '1'
        int_list = []
        for j in range(len(internal)):
            index_begin = partner_names.index(internal[j])
            if type(t[index_begin]) == str:
                t[index_begin] = re.sub('[+]', '', t[index_begin])
            num_int = t[index_begin:index_begin + 5]
            int_list.append(num_int)
        
            intlist2 = []
            for i in range(len(int_list)):
                for k in int_list[i]:
                    if type(k) == str:
                        k = re.sub('[+]', '', k)
                        k = float(k)
                    intlist2.append(k)
            intlist3 = []
            for i in range(0, len(intlist2), 5):
                num5 =  intlist2[i:i + 5]
                intlist3.append(num5)
                
        for i in range(len(resp_list)):
            if type(resp_list[i]) == str:
                resp_list[i] = resp_list[i].strip()
            
        new_dict['internal_interactions'] = []
        for i in range(len(internal)):
            dictint = {}
            dictint['mode2'] = []
            dictint['initiate2'] = []
            name = internal[i]
            dictint[name] = {}
            dictint[name]['content'] =intlist3[i]
            for j in range(len(resp_list)):
                if resp_list[j] in internal:
                    dictint['mode2'].append(mode[j])
                    dictint['initiate2'].append(initiate[j])
            dictint[name]['modes'] = dictint['mode2'][i]
            dictint[name]['initiating'] = dictint['initiate2'][i]
            del(dictint['mode2'])
            del(dictint['initiate2'])
            new_dict['internal_interactions'].append(dictint)

        master_dict['people'].append(new_dict)
    return(master_dict)

dict1 = masterdict_2017(survey_answers, partner_names)

#south africa
filename = folder + "/jan17_SA.xlsx"

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/jan17_SA.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = 'D:\\Dropbox\\NorthStar\\Havi\\jan17_SA.xlsx'
    s = wb.sheet_by_index(0)
    
raw_data = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    raw_data.append(row_list)


## Storing cleaned data into dictionary

# First row is used for reference 
var_names = raw_data[0]
#partner names are stored in the second row. 
partner_names = raw_data[1]

# Rest is raw data
survey_answers = raw_data[2:]

index_name = var_names.index('Q6')
index_partners = var_names.index('Q3_1_114_South Africa') # finds where the partner names start
index_partners_added = var_names.index('Q3_91_TEXT_South Africa') 
index_nsrate = var_names.index('Q8_1') 
resource_provided_index = var_names.index('Q12_x1_1_South Africa')
resource_provided_added = var_names.index('Q12_x91_TEXT_South Africa')
having_interacted_index = var_names.index('Q14')
nb_intra_interaction_index = var_names.index('Q16_x1_3') #number of interactions with people listed
other_int = var_names.index('Q18')
interaction_mode_index = var_names.index('Q20_x1')
other_mode = var_names.index('Q22')
interaction_initiation_index = var_names.index('Q24_x1')
region_index = var_names.index('region')

dict2 = masterdict_2017(survey_answers, partner_names)

#adding in global
filename = folder + "/data_17.xlsx"

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/data_17.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = 'D:\\Dropbox\\NorthStar\\Havi\\data_17.xlsx'
    s = wb.sheet_by_index(0)
    
raw_data = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    raw_data.append(row_list)

## Storing cleaned data into dictionary

# First row is used for reference 
var_names = raw_data[0]
#partner names are stored in the second row. 
partner_names = raw_data[1]

# Rest is raw data
survey_answers = raw_data[2:]

nb_partner_limit = 30 # current number of allowed partners
index_name = var_names.index('Q6')
index_partners = var_names.index('Q3_1_114_HQ') # finds where the partner names start
index_partners_added = var_names.index('Q3_46_TEXT_HQ') 
index_nsrate = var_names.index('Q8_1') 
resource_provided_index = var_names.index('Q12_x1_1_HQ')
resource_provided_added = var_names.index('Q12_x46_TEXT_HQ')
having_interacted_index = var_names.index('Q14_1')
nb_intra_interaction_index = var_names.index('Q16_x1_3_HQ') #number of interactions with people listed
other_int = var_names.index('Q18')
interaction_mode_index = var_names.index('Q20_x1_HQ')
other_mode = var_names.index('Q22')
interaction_initiation_index = var_names.index('Q24_x1_HQ')
region_index = var_names.index('region')

dict3 = masterdict_2017(survey_answers, partner_names)

#adding in RWCs

filename = folder + "/jan17_RWC.xlsx"

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/jan17_RWC.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = 'D:\\Dropbox\\NorthStar\\Havi\\jan17_RWC.xlsx'
    s = wb.sheet_by_index(0)
    
raw_data = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    raw_data.append(row_list)


## Storing cleaned data into dictionary

# First row is used for reference 
var_names = raw_data[0]
#partner names are stored in the second row. 
partner_names = raw_data[1]

# Rest is raw data
survey_answers = raw_data[2:]

nb_partner_limit = 30 # current number of allowed partners
index_name = var_names.index('Q6')
index_partners = var_names.index('Q3_1_114_RWCs') # finds where the partner names start
index_partners_added = var_names.index('Q3_108_TEXT_RWCs') 
index_nsrate = var_names.index('Q8_1') 
resource_provided_index = var_names.index('Q12_x1_1_RWCs')
resource_provided_added = var_names.index('Q12_x108_TEXT_RWCs')
having_interacted_index = var_names.index('Q14_1')
nb_intra_interaction_index = var_names.index('Q16_x1_3') #number of interactions with people listed
other_int = var_names.index('Q18')
interaction_mode_index = var_names.index('Q20_x1')
other_mode = var_names.index('Q22')
interaction_initiation_index = var_names.index('Q24_x1')
region_index = var_names.index('region')

dict4 = masterdict_2017(survey_answers, partner_names)

master_dict
with open(folder + 'dictionary_outputjan2017_v2.txt', 'wt') as out:
    pprint(master_dict, stream=out)
