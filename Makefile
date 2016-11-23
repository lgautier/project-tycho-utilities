BASENAME = ProjectTycho_Level2_v1.1.0
BASEURL = http://www.healthdata.gov/sites/default/files
DBNAME ?= tycho.db

%_0.zip :
	wget -q --show-progress ${BASEURL}/$@

%.csv.gz : %_0.zip
	unzip $< && rm $<
	gzip $*.csv

$(DBNAME) : $(BASENAME).csv.gz
	python3 tycho_sqlite.py -o ${DBNAME}

all: $(DBNAME)
