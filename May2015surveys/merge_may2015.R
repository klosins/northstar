library(readr)
library(tidyverse)
library(dplyr)
library(plyr)
library(data.table)

emplist2015 = read.csv("~/Dropbox/NorthStar/Havi/site_coord_hst.csv", quote="\"", comment.char="")

files <- list.files(path = "~/Dropbox/NorthStar/Havi/May2015surveys", pattern = "*.csv", full.names = T)
tbl <- sapply(files, read_csv, simplify=FALSE)
#Use gsub to get the names of the partners from the first row of each datatable. 
#gsub("^.*?-","-","For each of the partners below, select the year when the / partnership was first established with y...-Partner 5")
#tb = cd[1,]
#x = grep("Q3" , colnames(tb))
#tb[x[1]:x[length(x)]] <- gsub("^.*?-","-",tb[x])
updatenames2015 = function(datatable, area){
  x = grep("Q1" , colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  tb = datatable[1,]
  x = grep("Q3" , colnames(tb))
  y = grep("Q1" , colnames(tb))
  tb[x[1]:x[length(x)]] <- gsub("^.*?-","",tb[x])
  tb[y[1]:y[length(y)]] <- gsub("^.*?-","",tb[y])
  datatable[1,] = tb
  x = grep("Q3" , colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  subs <- subset(emplist2015, emplist2015$Location == area)
  datatable$RecipientLastName <- subs$Last.Name.s. 
  datatable$RecipientFirstName <- subs$First.Name.s. 
  datatable$region <- area
  #datatable = datatable[c(2),]
  #keeping first 2 observations
  datatable = datatable[c(1,2),]
  dataret <<- datatable
}

listsofregions2015 <- vector("list", 24)
j =  c("Beitbridge", "Bloemfontein", "Bloemhof", "Burnt Forest", "Cato Ridge", "Chirundu North", "Chirundu South",  "Emali","Ficksburg", "Forbes", "Kazangula", "Maai Mahiu", "Matsapha", "Mlolongo", "Mombasa", "Musina", "Mwanza", "Namanga", "Ngodwana", "Ngwenya", "Pomona", "Pongola", "Salgaa", "Victoria Falls" )

for(i in 1:24){
  listsofregions2015[[i]] = updatenames2015(tbl[[i]], j[i])
}
may2015 = bind_rows(listsofregions2015 )

write.csv(may2015 ,'may2015_2.csv')