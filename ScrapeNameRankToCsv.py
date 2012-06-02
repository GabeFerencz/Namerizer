#!/usr/bin/env python
#Gabe Ferencz

import urllib2, csv
from BeautifulSoup import BeautifulSoup

YEAR_MIN = 2000
YEAR_MAX = 2010 # social security site usually goes to the previous year
STATE = 'NY'

bnames = {}
gnames = {}

class BabyName(object):
    def __init__(self, name, sex, meaning = ''):
        self.sex = sex
        self.name = name
        self.usRank = {} #get(key[, default])
        self.usPct = {}
        self.stateRank = {}

    def updateRankUs(self,year,rank):
        self.usRank[year] = rank
    
    def updateRankState(self,year,rank):
        self.stateRank[year] = rank

    def updatePctUs(self,year,pct):
        self.usPct[year] = pct

    def emit_csv_line(self):
        return [self.name,self.sex,self.usRank,self.usPct,self.stateRank]

def get_record(page,data):
    record = []
    print 'Scraping:',page,data
    resp = urllib2.urlopen(page,data)
    bsoup = BeautifulSoup(resp.read())
    table = bsoup.findAll('table')[1]
    rows = table.findAll('tr')
    for row in rows:
        cols = row.findAll('td')
        if len(cols) == 5:
            rank = cols[0].string
            bname = cols[1].string
            bcnt = cols[2].string
            gname = cols[3].string
            gcnt = cols[4].string
            record.append(';'.join([rank, bname, bcnt, gname, gcnt]))
    return '\n'.join(record)

def scrape_over_years(years):
    pageUS = 'http://www.ssa.gov/cgi-bin/popularnames.cgi'
    dataUS = 'year=%d&top=1000&number=p'

    pageState = 'http://www.ssa.gov/cgi-bin/namesbystate.cgi'
    dataState = 'state=%s&year=%d'

    for year in years:
        usData = get_record(pageUS,dataUS%year)
        stateData = get_record(pageState,dataState%(STATE,year))
        for ud in usData.split('\n'):
            entry = ud.split(';')
            rank = int(entry[0])
            bname = entry[1]
            bpct = entry[2]
            gname = entry[3]
            gpct = entry[4]
            if bname not in bnames:
                bnames[bname] = BabyName(bname,'boy')
            if gname not in gnames:
                gnames[gname] = BabyName(gname,'girl')
            bnames[bname].updateRankUs(year,rank)
            bnames[bname].updatePctUs(year,bpct)
            gnames[gname].updateRankUs(year,rank)
            gnames[gname].updatePctUs(year,gpct)
        for sd in stateData.split('\n'):
            entry = sd.split(';')
            rank = int(entry[0])
            bname = entry[1]
            gname = entry[3]
            if bname not in bnames:
                bnames[bname] = BabyName(bname,'boy')
            if gname not in gnames:
                gnames[gname] = BabyName(gname,'girl')
            bnames[bname].updateRankState(year,rank)
            gnames[gname].updateRankState(year,rank)
    print 'Loaded %d boy\'s names.'%len(bnames)
    print 'Loaded %d girl\'s names.'%len(gnames)

def save_baby_name_ranks():
    gfile = open('girlNameRanks%s.csv'%STATE,'wb')
    bfile = open('boyNameRanks%s.csv'%STATE,'wb')
    gwriter = csv.writer(gfile)
    bwriter = csv.writer(bfile)
    gwriter.writerow(['name','gender','usRank','usPct','stateRank'])
    bwriter.writerow(['name','gender','usRank','usPct','stateRank'])
    for g in gnames.values(): gwriter.writerow(g.emit_csv_line())
    for b in bnames.values(): bwriter.writerow(b.emit_csv_line())
    gfile.close()
    bfile.close()

def test_scrape():
    from TestSuite import scrape_2010_US_1000_p
    rslt = get_record('http://www.ssa.gov/cgi-bin/popularnames.cgi',
                    'year=2010&top=1000&number=p')
    print rslt.split('\n')[:5]
    print rslt.split('\n')[-5:]
    assert rslt == scrape_2010_US_1000_p, 'Not done yet!'

if __name__ == "__main__":
    #test_scrape()
    scrape_over_years(range(YEAR_MIN,YEAR_MAX+1))
    save_baby_name_ranks()

