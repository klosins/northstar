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
import copy
import pandas
from pprint import pprint

config_path = os.path.join("/Users/hsheldah/Dropbox/NorthStar/Havi")
os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi')

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    folder = '/Users/hsheldah/Dropbox/NorthStar/Havi'
else:
    folder = 'D:\\Dropbox\\NorthStar\\Havi'

filename = folder + "/Jun2016surveys/NSA-survey-download-20160830_hst.xlsm"

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/Jun2016surveys/NSA-survey-download-20160830_hst.xlsm')
    s = wb.sheet_by_index(0)
else:
    wb = 'D:\\Dropbox\\NorthStar\\Havi\\Jun2016surveys\\NSA-survey-download-20160830_hst.xlsm'
    s = wb.sheet_by_index(0)

raw_data = []
for row in range(s.nrows):
    row_list = []
    for col in range(s.ncols):
        row_list.append(s.cell(row,col).value)
    raw_data.append(row_list)

## Creating a matching dictionary for names
# Three files have relevant information on this:
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

# I created this file because some names aren't correctly matched
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

# Combining the two enables us to convert the name they give us into the name we have
# in the list of contacts
names_dict = {key: group_emails_dict[respondent_dict[key]] for key in respondent_dict if respondent_dict[key] in group_emails_dict}

names_dict = {**names_dict, **missing_dict} # combines the dictionaries

## Storing cleaned data into dictionary

# First row is used for reference (second row is ignored)
var_names = raw_data[0]

# Rest is raw data
survey_answers = raw_data[2:]

## Fixed parameters, indexes and lists for reference in loop

nb_partner_limit = 30 # current number of allowed partners
index_partners = var_names.index('QID3_51') # finds where the partner names start
nb_interactions_index = var_names.index('QID16_x51_114')
partner_type_index = var_names.index('QID7_x51')
resource_need_index = var_names.index('QID17_1')
resource_provided_index = var_names.index('QID1_1_x51')
having_interacted_index = var_names.index('QID4_99')
having_interacted_indexlast = var_names.index('QID4_120') # index of last person
nb_intra_interaction_index = var_names.index('QID19_x99_3')
interaction_mode_index = var_names.index('QID14_x99')
interaction_initiation_index = var_names.index('QID23_x99')

partner_categories = [] # Find all possible types of partners
for row in survey_answers:
    for i in range(nb_partner_limit):
        types = row[partner_type_index + i*2].split(',')
        for type in types:
            if type not in partner_categories and type != '':
                partner_categories.append(type)
partner_categories.sort()


resource_categories = [] # Find all possible types of resources
for i in range(6):
    # raw_data[1] has the name of resources (it's part of the question)
    type = raw_data[1][resource_need_index + i] 
    resource_categories.append(type.split(' - ')[1])
# Do not sort this list! References to resources will appear in the same order

intra_interaction_categories = [] # Find all possible types of resources
for i in range(5):
    # raw_data[1] has the name of resources (it's part of the question)
    type = raw_data[1][nb_intra_interaction_index + i] 
    intra_interaction_categories.append(type.split(' - ')[1])
# Do not sort this list! References to interaction types will appear in the same order

interaction_mode_categories = ['Text (email, SMS, Facebook, WhatsApp...)',
                               'Audio-visual (Telephone, Skype...)',
                               'In person']


# Create main dictionary
master_dict = {}
master_dict['people'] = []
# ... which is made of dictionaries for each person
for row in survey_answers:
    person_dict = {}
    # data are found by referring to the columns with specific titles in the file
    person_dict['name'] = row[var_names.index('QID28_1')] # ... e.g. 'QID28_1'
    person_dict['region'] = row[var_names.index('QID29')]
    ## Partners
    person_dict['partners'] = []
    for i in range(nb_partner_limit):
        if len(row[index_partners + i]) > 0:
            person_dict['partners'].append({})
            person_dict['partners'][-1]['name'] = row[index_partners + i]
    # Number of interactions with partners
    person_dict['nb_partners'] = len(person_dict['partners'])
    for i in range(person_dict['nb_partners']):
        person_dict['partners'][i]['nb_interactions'] = row[nb_interactions_index + 2*i]
        partner_type = []
        for type in partner_categories:
            partner_type.append((type in row[partner_type_index + 2*i].split(','))*1)
        person_dict['partners'][i]['partner_type'] = partner_type
    person_dict['resources_available'] = []
    # Resources available
    for i in range(len(resource_categories)):
        # need to convert into number (instead of '7: Strongly Agree'):
        number = int(str(row[resource_need_index + i])[0])
        person_dict['resources_available'].append(number)
    # Resources provided by partners
    for i in range(len(resource_categories)):
        for j in range(person_dict['nb_partners']):
            if 'resources_provided' not in person_dict['partners'][j]:
                person_dict['partners'][j]['resources_provided'] = []
            number = row[resource_provided_index + nb_partner_limit*i + j]
            if number == '':
                number = 0
            # numbers mean 'this partner provides x percent of this resource'
            person_dict['partners'][j]['resources_provided'].append(number)
    ## Interactions with colleagues
    person_dict['internal_interactions'] = {}
    # for each colleague, create a dictionary if they interact
    for i in range(having_interacted_indexlast - having_interacted_index):
        person_name = raw_data[1][having_interacted_index + i].split(' - ')[-1]
        if row[having_interacted_index + i] != '': # if interact
            person_dict['internal_interactions'][person_name] = {}
            # for each type of interaction
            person_dict['internal_interactions'][person_name]['content'] = []
            for j in range(len(intra_interaction_categories)):
                content = row[nb_intra_interaction_index + i * len(intra_interaction_categories) + j]
                if content == '':
                    content = 0
                elif isinstance(content, str):
                    content = 1 # if other string, then they interacted once(e.g. 'CONFERENCE')
                elif content > 40000:
                    excel_date = xldate_as_tuple(content, 0)[1:3]
                    content = np.mean(excel_date)
                person_dict['internal_interactions'][person_name]['content'].append(content)
            # modes of communication
            interaction_modes = []
            for mode in interaction_mode_categories:
                dummy = (mode in row[interaction_mode_index+i])*1
                interaction_modes.append(dummy)
            person_dict['internal_interactions'][person_name]['modes'] = interaction_modes
            # initiating the interaction
            initiation = int(str(row[interaction_initiation_index + i])[0])
            person_dict['internal_interactions'][person_name]['initiating'] = initiation
            
    master_dict['people'].append(person_dict)

#replacing names:
for entry in master_dict['people']:
    if entry['name'] == 'Cathy':
        entry['name'] = 'Cathy Jongens'
    if entry['name'] == 'lucas Pinxten':
        entry['name'] = 'Lucas Pinxten'
    if entry['name'] == 'Eva':
        entry['name'] = 'Eva Mwai'
    if entry['name'] == 'OSBORNE NDALO': 
        entry['name'] = 'Osborne Ndalo'
    if entry['name'] == 'Dr Richard Ayebare': 
        entry['name'] = 'Richard Ayebare'
    if entry['name'] == 'samuel': 
        entry['name'] = 'Samuel Kinyanjui'
    if entry['name'] == 'Eston Njagi': 
        entry['name'] = 'Eston Njagi Nyaga'
    if entry['name'] == 'Nyabuto Barongo':
        entry['name'] = 'Nyabuto (Osoro) Barongo'
    if entry['name'] == 'Osoro Nyabuto Barongo':
        entry['name'] = 'Nyabuto (Osoro) Barongo'
    if entry['name'] == 'Jacob Okoth':  
        entry['name'] = 'Jacob Okoth Odhiambo'
    if entry['name'] == 'Esther': 
        entry['name'] = 'Esther Muigai'
    if entry['name'] == 'Esther Muighai':
        entry['name'] = 'Esther Muigai'
    if entry['name'] == 'john mochama':
        entry['name'] = 'John Mochama'
    if entry['name'] == 'THANDEKA KHOZA':
        entry['name'] = 'Thandeka Khoza'
    if entry['name'] == 'Maud':
        entry['name'] = 'Maud Mogale'
    if entry['name'] == 'Lorayne':
        entry['name'] = 'Lorayne Pillay'
    if entry['name'] == 'AndrÃ© Oosthuizen':
        entry['name'] = 'Andre Oosthuizen'
    if entry['name'] == 'André Oosthuizen':
        entry['name'] = 'Andre Oosthuizen'
    if entry['name'] == 'ROZAAN':
        entry['name'] = 'Rozaan van der Westhuysen'
    if entry['name'] == 'Thandi':
        entry['name'] = 'Thandi Manzini'
    if entry['name'] == 'Sibonelo Khomo':
        entry['name'] = 'Sibonelo Sifisukuthula Khomo'
    if entry['name'] == 'TE Morapeli':
        entry['name'] = 'Thapelo Morapeli'
    if entry['name'] == 'Preggie':
        entry['name'] = 'Preggie Pillay'
    if entry['name'] == 'kibet':
        entry['name'] = 'Kibet Cgerongis'
    if entry['name'] == 'STEVEN MHANDO':
        entry['name'] = 'Steven Mhando'
    if entry['name'] == 'Emmanuel lemein':
        entry['name'] = 'Emmanuel Lemein'
    if entry['name'] == 'Charles':
        entry['name'] = 'Charles Ojullo'
    if entry['name'] == 'STEPHEN GICHINA':
        entry['name'] = 'Stephen Gichina'
    if entry['name'] == 'Shumba':
        entry['name'] = 'Nyarai Shumba'
    if entry['name'] == 'Bronwyn Cawood ':
        entry['name'] = 'Bronwyn Cawood'
    if entry['name'] == 'Eston Njagi Nyaga':
        entry['name'] = 'Eston Njagi'
    if entry['name'] ==  'Kibet Cgerongis':
        entry['name'] = 'Kibet Cherongis'
    if entry['name'] ==  'Oliver  Simiyu':
        entry['name'] = 'Oliver Simiyu'
    if entry['name'] ==  'Sibonelo Sifisukuthula Khomo':
        entry['name'] = 'Sibonelo Khomo'
        print(entry['name'])

#replacing region for those with RWC listed.
for entry in master_dict['people']:
    if  entry['name'] == 'Nyarai Shumba':
            entry['region'] = 'Regional: South Africa'
    if entry['name'] == 'Makalo Moses Nathane':
            entry['region'] = 'Regional: South Africa'
    if  entry['name'] == 'Oliver Simiyu':
            entry['region'] = 'Regional: East Africa'
    if  entry['name'] == 'NICK NYANDIKA SITIMA':
            entry['region'] = 'Regional: East Africa'
    if entry['name'] == 'Stephen Gichina':
            entry['region'] = 'Regional: East Africa'
    if  entry['name'] == 'Charles Ojullo':
            entry['region'] = 'Regional: East Africa'
    if entry['name'] == 'Emmanuel Lemein':
            entry['region'] = 'Regional: East Africa'
    if entry['name'] == 'Centinary Gervase':
            entry['region'] = 'Regional: East Africa'
    if entry['name'] == 'Steven Mhando':
            entry['region'] = 'Regional: East Africa'
    if entry['name'] == 'Jenifer Tavengerwei':
            entry['region'] = 'Regional: South Africa'
    if entry['name'] == 'Jabulani Makhiya':
            entry['region'] = 'Regional: South Africa'
    if  entry['name'] == 'Kibet Cherongis':
            entry['region'] = 'Regional: East Africa'
    if  entry['name'] == 'Juliana Muskwe':
            entry['region'] = 'Regional: South Africa'



#accessing individual names
master_dict['people'][2]['name']

#creating dictionary for workers under Eva Mwai
master_dict2 = {}
master_dict2["children"] = []
master_dict2["region"] = []
master_dict2["children"] = []

for entry in master_dict["people"]:
    person_dict2 = {}
    person_dict2["name"] = entry["name"] 
    person_dict2["region"] = entry["region"]
    person_dict2["children"] = []
    for ent in entry["partners"]:
        person_dict3 = {}
        person_dict3["name"] = ent["name"]
        person_dict2["children"].append(person_dict3)
    master_dict2["children"].append(person_dict2)

eva_dict2 = {} 
eva_dict2["children"] = []
for d in master_dict2['children']:
    if d['region'] == 'Regional: East Africa' and d['name'] != 'Eva Mwai':
        person_dicteva = {}
        print(d["name"])
        person_dicteva["name"] = d["name"] 
        person_dicteva["region"] = d["region"]
        person_dicteva["children"] = []
        for ent in d["children"]:
            person_dicteva2 = {}
            person_dicteva2["name"] = ent["name"]
            person_dicteva["children"].append(person_dicteva2)
        eva_dict2['children'].append(person_dicteva)
#deleting key for region       
for d in eva_dict2['children']:
    del(d['region'])

for x in   eva_dict2['children']:
    if x['name'] == "Esther Muigai":
        del(x['children'])


#deleting key for children for Esther Muigai (she doesn't have any external partners)
eva_dict3 = {} 
eva_dict3["name"] = ['Eva Mwai']
eva_dict3["name"].append(eva_dict2)

eva_dict3

#creating paul dictionary
    
paul_dict = {} 
paul_dict["children"] = []
for d in master_dict2['children']:
    if d['region'] == 'Regional: South Africa' and d['name'] != 'Paul Matthew':
        person_dictpaul = {}
        print(d["name"])
        person_dictpaul["name"] = d["name"] 
        person_dictpaul["region"] = d["region"]
        person_dictpaul["children"] = []
        for ent in d["children"]:
            person_dictpaul2 = {}
            person_dictpaul2["name"] = ent["name"]
            person_dictpaul["children"].append(person_dictpaul2)
        paul_dict['children'].append(person_dictpaul)
#deleting key for region       
for d in paul_dict['children']:
    del(d['region'])

paul_dict2 = {} 
paul_dict2["name"] = ['Paul Matthew']
paul_dict2["name"].append(paul_dict)

paul_dict2

#combining under Ylse
ylse_dict = {} 
ylse_dict["children"] = []
ylse_dict["children"].append(eva_dict3)
ylse_dict["children"].append(paul_dict2)

ylse_dict2 = {} 
ylse_dict2["name"] = ['Ylse van der Schoot']
ylse_dict2["name"].append(ylse_dict)


import json
print(json.dumps(ylse_dict2))

#code for Getting list of names by region
#for d in master_dict2['children']:
  #  if d['region'] == 'Regional: East Africa':
    #    print(d["name"])


