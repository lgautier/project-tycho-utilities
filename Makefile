BASENAME=ProjectTycho_Level2_v1.1.0
BASEURL=http://www.healthdata.gov/sites/default/files

$(BASENAME)_0.zip :
  wget ${BASEURL}/$<

$(BASENAME).csv.gz:
  unzip ${BASENAME}_0.zip && rm ${BASENAME}_0.zip
  gzip ${BASENAME}.csv
  
all: $(BASENAME).csv.gz
