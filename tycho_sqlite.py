##
## Build and SQLite3 database from Level 2 data
## in Project Tycho.
##
## Data from Project Tycho is not provided, by is availale under
## a Creative Common Public License or an
## Open Data Commons Open Database License (ODbL)
##
## Reference for Project Tycho:
##
## Willem G. van Panhuis, John Grefenstette, Su Yon Jung, Nian Shong Chok,
## Anne Cross, Heather Eng, Bruce Y Lee, Vladimir Zadorozhny, Shawn Brown,
## Derek Cummings, Donald S. Burke. Contagious Diseases in the United States
## from 1888 to the present. NEJM 2013; 369(22): 2152-2158.
##

import csv, gzip, sqlite3, os, sys

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o',
                   required=True,
                   help='Output file')
args = parser.parse_args()

input_tycho_filename = 'ProjectTycho_Level2_v1.1.0.csv.gz'

output_filename = args.o

print('Creating database in %s' % output_filename)

if os.path.exists(output_filename):
    print('The output file %s is already present. '
          '(Re)move if you want to rebuild the database.' % output_filename)
    print('Bye.')
    sys.exit(1)

print('Creating the schema...', end='', flush=True)
dbcon = sqlite3.connect(output_filename)
cursor = dbcon.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS location (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  city VARCHAR,
  state VARCHAR);
""")
cursor.execute("""
CREATE INDEX loc_state_idx ON location(state);
""")
cursor.execute("""
CREATE INDEX loc_city_idx ON location(city);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS disease (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR);
""")

sql = '''
INSERT INTO disease (
 name
) VALUES (
  ?
)'''
cursor.execute("""
CREATE INDEX disease_name_idx ON disease(name);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS casecount (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  location_id INTEGER,
  count INTEGER,
  date_from TEXT,
  date_to TEXT,
  epiweek INTEGER,
  disease_id INTEGER,
  FOREIGN KEY(location_id) REFERENCES location(id),
  FOREIGN KEY(disease_id) REFERENCES disease(id)
);
""")

print('done.')

sql = '''
INSERT INTO casecount (
 location_id,
 count,
 date_from,
 date_to,
 epiweek,
 disease_id
) VALUES (
  ?,
  ?,
  DATE(?),
  DATE(?),
  ?,
  ?
)'''

sql_insertlocation = 'INSERT INTO location (city, state) VALUES (?, ?)'
sql_insertdisease = 'INSERT INTO disease (name) VALUES (?)'
PROGRESS = int(10000)
print('Inserting the data...')
with gzip.open(input_tycho_filename, 'rt') as fh_in:
    csv_r = csv.reader(fh_in)
    loc_ids = dict()
    disease_ids = dict()
    header = next(csv_r)
    epiweek_i = header.index('epi_week')
    datefrom_i = header.index('from_date')
    dateto_i = header.index('to_date')
    state_i = header.index('state')
    loc_i = header.index('loc')
    loctype_i = header.index('loc_type')
    disease_i = header.index('disease')
    number_i = header.index('number')
    ## epi_week,country,state,loc,loc_type,disease,
    ## event,number,from_date,to_date,url
    for row_i, row in enumerate(csv_r):
        state = row[state_i]
        if row[loctype_i] == 'CITY':
            city = row[loc_i]
        else:
            city = None
        if (state, city) not in loc_ids:            
            cursor.execute(sql_insertlocation, (city, state))
            loc_ids[(state,city)] = cursor.lastrowid
        count = row[number_i]
        datefrom = row[datefrom_i]
        dateto = row[dateto_i]
        epiweek = row[epiweek_i]
        disease = row[disease_i]
        if disease not in disease_ids:
            cursor.execute(sql_insertdisease, (disease,))
            disease_ids[disease] = cursor.lastrowid
        cursor.execute(sql,
                       (loc_ids[(state, city)],
                        count,
                        datefrom,
                        dateto,
                        epiweek,
                        disease_ids[disease]))
        if (row_i % PROGRESS) == 0:
            print('\r row {:,}'.format(row_i), end='', flush=True)
print('\r row %i' % row_i)
print('Done.')
dbcon.commit()
cursor.close()
dbcon.close()
