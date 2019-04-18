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
#import pexpect
import subprocess
import csv
import shutil
import collections
import copy
import pandas
from pprint import pprint

#This is only for the global excel file. 

config_path = os.path.join("/Users/hsheldah/Dropbox/NorthStar/Havi")
os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi')

if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    folder = '/Users/hsheldah/Dropbox/NorthStar/Havi'
else:
    folder = 'D:\\Dropbox\\NorthStar\\Havi'

filename = folder + "/data_2017.xlsx"


if os.path.exists('/Users/hsheldah/Dropbox/NorthStar/Havi'):
    wb = open_workbook('/Users/hsheldah/Dropbox/NorthStar/Havi/data_2017.xlsx')
    s = wb.sheet_by_index(0)
else:
    wb = 'D:\\Dropbox\\NorthStar\\Havi\\Jun2016surveys\\data_2017.xlsx'
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

survey_answers = raw_data[2:]

## Fixed parameters, indexes and lists for reference in loop

nb_partner_limit = 30 # current number of allowed partners

index_partners = var_names.index('Q3_1_114_HQ') # finds where the partner names start
index_partners_added = var_names.index('Q3_46_TEXT_HQ') 
index_nsrate = var_names.index('Q8_1') 
resource_provided_index = var_names.index('Q12_x1_1_HQ')
having_interacted_index = var_names.index('Q14_1')
nb_intra_interaction_index = var_names.index('Q16_x1_3') #number of interactions with people listed
interaction_mode_index = var_names.index('Q20_x1')
interaction_initiation_index = var_names.index('Q24_x1')

resource_categories = ['Financial Support', 'Equipment / supplies', 'Human Resources', 'Information / Expertise', 'Legitimacy / Reputation', 'Advertising / referrals', 'Other']

intra_interaction_categories = ['Socializing / Interpersonal', 'Partnerships', 'Technical (e.g., functioning of COMETs)', 'Healthcare Information','Other (please specify in the comments section below)']

interaction_mode_categories = ['Text (email, SMS, Facebook, WhatsApp...)',
                               'Audio-visual (Telephone, Skype...)',
                               'In person']

# Create main dictionary
master_dict = {}
master_dict['people'] = []
    
