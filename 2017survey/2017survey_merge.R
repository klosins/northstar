#merging 2017 files

files <- list.files(path = "~/Dropbox/NorthStar/Havi/2017survey", pattern = "*.csv", full.names = T )
tbl <- sapply(files, read_csv, simplify=FALSE)

listsofregions2017 <- vector("list", 4)
for(i in 1:4){
  data = as.data.frame(tbl[[i]])
  data = data[-c(1,2),]
  listsofregions2017[[i]] =  data
}

survey2017 = bind_rows(listsofregions2017)

write.csv(survey2017,'survey2017.csv')

updatenames2017 = function(datatable, area){
  datatable = datatable[-c(2),]
  x = grep("Q3" , colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  tb = datatable[1,]
  x = grep("Q3" , colnames(tb))
  y = grep("Q12" , colnames(tb))
  tb[x[1]:x[length(x)]] <- gsub("^.*?-","",tb[x])
  tb[y[1]:y[length(y)]] <- gsub("^.*?-","",tb[y])
  datatable[1,] = tb
  x = grep("Q12" , colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  datatable$region <- area
  
  x = grep("Q3", colnames(datatable))
  y = grep("Q12", colnames(datatable))
  z = grep("Q16", colnames(datatable))
  w = grep("Q20", colnames(datatable))
  v = grep("Q24", colnames(datatable))
  
  tb = datatable[1,]
  #run the following command 4 times.
  for ( i in 1:4){
  tb[x[1]:x[length(x)]] <- gsub("^.*?.edu -","",tb[x])
  }
  
  #Then run this once
  tb[x[1]:x[length(x)]] <- gsub("- N.*","",tb[x])
  
  #run this 3 times
  for (i in 1:3){
  tb[y[1]:y[length(y)]] <- gsub("^.*?-","",tb[y])}

  #run this once
  tb[y[1]:y[length(y)]] <- gsub("\\-.*","",tb[y])
  
  #run this 3 times
  for (i in 1:3){
  tb[z[1]:z[length(z)]] <- gsub("^.*?-","",tb[z])}

  #run this once
  tb[z[1]:z[length(z)]] <- gsub("\\-.*","",tb[z])
  #will need to update names of Susan-Mary Foster, Sylvia Mushumba-Barure, because the code removed their last names
  
  tb[w[1]:w[length(w)]] <- gsub("^.*?-","",tb[w])
  tb[v[1]:v[length(v)]] <- gsub("^.*?-","",tb[v])
  datatable[1,] = tb
  datatable[is.na(datatable)] <- 0
  dataret <<- datatable

}

listsofregions2017 <- vector("list", 4)
j =  c("HQ", "East Africa", "South Africa", "RWCs")
for(i in 1:4){
  listsofregions2017[[i]] = updatenames2017(tbl[[i]], j[i])
}
jan2017 = bind_rows(listsofregions2017 )
#below code gets rid of unfinished responses - for global
updatenames2017(tbl[[1]], j[1])
row_sub = apply(dataret['Finished'], 1, function(row) all(row != 'FALSE' ))
dataret = dataret[row_sub,]
write.csv(dataret ,'jan17_HQ.csv')

#below code gets rid of unfinished responses - for east africa
updatenames2017(tbl[[2]], j[2])
row_sub = apply(dataret['Finished'], 1, function(row) all(row != 'FALSE' ))
dataret = dataret[row_sub,]
write.csv(dataret ,'jan17_EA.csv')

#for south africa;
updatenames2017(tbl[[3]], j[3])
row_sub = apply(dataret['Finished'], 1, function(row) all(row != 'FALSE' ))
dataret = dataret[row_sub,]
write.csv(dataret ,'jan17_SA.csv')




updatenames2017_rwcs = function(datatable, area){
  datatable = datatable[-c(2),]
  x = grep("Q3" , colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  tb = datatable[1,]
  x = grep("Q3" , colnames(tb))
  y = grep("Q12" , colnames(tb))
  tb[x[1]:x[length(x)]] <- gsub("^.*?-","",tb[x])
  tb[y[1]:y[length(y)]] <- gsub("^.*?-","",tb[y])
  datatable[1,] = tb
  x = grep("Q12" , colnames(datatable))
  colnames(datatable)[x[1]:x[length(x)]] <- paste(colnames(datatable)[x[1]:x[length(x)]], area, sep = "_")
  datatable$region <- area
  
  x = grep("Q3", colnames(datatable))
  y = grep("Q12", colnames(datatable))
  z = grep("Q16", colnames(datatable))
  w = grep("Q20", colnames(datatable))
  v = grep("Q24", colnames(datatable))
  
  tb = datatable[1,]
  #run the following command 4 times.
  for ( i in 1:4){
    tb[x[1]:x[length(x)]] <- gsub("^.*?.edu -","",tb[x])
  }
  
  #Then run this once
  tb[x[1]:x[length(x)]] <- gsub("- N.*","",tb[x])
  
  #run this 3 times
  for (i in 1:3){
    tb[y[1]:y[length(y)]] <- gsub("^.*?-","",tb[y])}
  
  #run this once
  tb[y[1]:y[length(y)]] <- gsub("\\-.*","",tb[y])
  
  #run this 3 times
  for (i in 1:5){
    tb[z[1]:z[length(z)]] <- gsub("^.*?-","",tb[z])}
  
  #run this once
  tb[z[1]:z[length(z)]] <- gsub("\\-.*","",tb[z])
  #will need to update names of Susan-Mary Foster, Sylvia Mushumba-Barure, because the code removed their last names
  
  tb[w[1]:w[length(w)]] <- gsub("^.*?-","",tb[w])
  tb[v[1]:v[length(v)]] <- gsub("^.*?-","",tb[v])
  datatable[1,] = tb
  datatable[is.na(datatable)] <- 0
  dataret <<- datatable
  
}

#For RWCs
updatenames2017_rwcs(tbl[[4]], j[4])
row_sub = apply(dataret['Finished'], 1, function(row) all(row != 'FALSE' ))
dataret = dataret[row_sub,]
write.csv(dataret ,'jan17_RWC.csv')

