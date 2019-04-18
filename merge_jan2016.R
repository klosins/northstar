#merging Jan 2016 files, adding coordinator names. Making sure all of the different partners are included.
library(readr)
library(tidyverse)
library(dplyr)
library(plyr)
library(data.table)

#importing list of employees by region
emplist = read.csv("~/Dropbox/NorthStar/Havi/Employee-List-NSA-July2016_hst.csv", quote="\"", comment.char="")
#only keeping names of coordinators/managers/outreach/etc by region:
emplistcoord <- emplist[emplist$Job.title  == "Site Coordinator" | emplist$Job.title  == "Lay Councellor" |emplist$Job.title  == "Outreach Coordinator"| emplist$Job.title  == "Project Manager" | emplist$Job.title  == "IEC/BCC Outreach", ]

#writing function to add in names and delete unnecessary rows
updatenames = function(datatable, area){
  x = grep("Q3", colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  subs <- subset(emplist, emplist$Location == area)
  datatable$RecipientLastName <- subs$Last.Name.s. 
  datatable$RecipientFirstName <- subs$First.Name.s. 
  datatable$region <- area
  datatable = datatable[-c(1,2),]
  dataret <<- datatable
}


files <- list.files(path = "~/Dropbox/NorthStar/Havi/Jan2016surveys", pattern = "*.csv", full.names = T)
tbl <- sapply(files, read_csv, simplify=FALSE)
emplist = read.csv("~/Dropbox/NorthStar/Havi/site_coord_hst.csv", quote="\"", comment.char="")

listsofregions <- vector("list", 17)
j =  c("Beitbridge", "Cato Ridge", "Chirundu South", "Dar es Salaam",  "Emali", "Farafenni", "Ficksburg", "Iringa",
     "Jomvu", "Katuna", "Maai Mahiu", "Mlolongo", "Mombasa", "Musina", "Namanga", "Ngwenya", "Tunduma")
for(i in 1:17){
  listsofregions[[i]] = updatenames(tbl[[i]], j[i])
}
jan2016 = bind_rows(listsofregions )

#binding now with HQ data
HQ = read.csv("~/Dropbox/NorthStar/Havi/regional online survey-Feb2016_December 14, 2017_16.17.csv", quote="\"", comment.char="")
x = grep("Q3", colnames(HQ))
colnames(HQ)[x[1]:x[length(x)]] <- paste(colnames(HQ)[x[1]:x[length(x)]], "HQ", sep = "_")
HQ = HQ[-c(1,2),]

jan2016 = bind_rows(jan2016, HQ)

#confirm who to use in employee data for Musina, Farafenni, Mlolongo (2 outreach coordinators in Employee List excel, no site coordinator).

#note that I deleted the first 2 rows from Beitbridge, the second response row from Dar Es Salaam (although the person indicated that they interacted with themself, this was the only one with a Jan 2016 date.  For Katuna, the person with the most responses indicated that they had interacted with the site coordinator (Centinary), so I deleted this response.
#for Ngwenya I deleted the second response row.  This was only because it had fewer observations, unsure how to tell since neither indicated they interacted with the site coordinator.
#also, for Farafenni I did not see a site coordinator listed in the employee list excel - According to Aline the coordinator is Samba


write.csv(jan2016,'jan2016.csv')

