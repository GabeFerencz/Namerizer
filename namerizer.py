#!/usr/bin/env python
#Gabe Ferencz

STATE = 'NY'
HELP_MENU = '''
Commands:
boy - prints info on random boy name from ranked entries
girl - prints info on random girl name from ranked entries
rand - prints info on random name (boy/girl also random) from ranked entries
names - prints out name and uniqueness for our boy and girl names
sorted - same as above, but sorted on uniqueness
reload - reloads the names from boyNames.txt and girlNames.txt

Variables:
boyNames - list of our choices of boy names
girlNames - list of our choices of girl names
boyNameDict - dictionary of ranked boy names, key is the name
girlNameDict - dictionary of ranked girl names, key is the name
'''.strip()

class RankedBabyName(object):
    def __init__(self, name, gender, usRank, usPct, stateRank, meaning = ''):
        self.gender = gender
        self.name = name
        self.usRank = eval(usRank)
        self.usPct = eval(usPct)
        self.stateRank = eval(stateRank)
        self.meaning = meaning
        years = map(int,self.usRank.keys())
        if years:
            self.minYear = min(years)
            self.maxYear = max(years)
        else:
            self.minYear = 1e1000
            self.maxYear = 0
        if self.stateRank:
            self.stateMax = max(map(int,self.stateRank.values()))
        else:
            self.stateMax = 0
        if self.usRank:
            self.usMax = max(map(int,self.usRank.values()))
        else:
            self.usMax = 0

    def uniqueness(self, usAdj = 1.0, stateAdj = 15.0, yAdj = 10.0):
        currentYear = YEAR_RANGE[0] + 1
        usScore = 0
        stateScore = 0
        bestCase = 0
        worstCase = 0
        bcVal = US_UNRANKED*usAdj + STATE_UNRANKED*stateAdj
        wcVal = usAdj + stateAdj
        for year in YEAR_RANGE:
            yearDiff = (currentYear - year + 1)*yAdj
            usScore += self.usRank.get(year,US_UNRANKED)*usAdj/yearDiff
            stateScore += self.stateRank.get(year,STATE_UNRANKED) * \
                            stateAdj/yearDiff
            bestCase += bcVal/yearDiff
            worstCase += wcVal/yearDiff
        return ((usScore+stateScore)-worstCase)/(bestCase-worstCase)

    def rank_table(self):
        col1=['%4d'%year for year in YEAR_RANGE]
        col2=['%4s'%str(self.usRank.get(year,'-')) for year in YEAR_RANGE]
        col3=['%4s'%str(self.stateRank.get(year,'-')) for year in YEAR_RANGE]
        col1.insert(0,'            Year:')
        col2.insert(0,'         US Rank:')
        col3.insert(0,'      State Rank:')
        return '\n'.join([' '.join(col1),' '.join(col2),' '.join(col3)])

    def __repr__(self):
        args = [self.name]
        args.append('%.2f%% unique'%(100*self.uniqueness()))
        if self.meaning is not '':
            args.append(self.meaning)
        return ' - '.join(args)

noRank = RankedBabyName('None','','{}','{}','{}')

def load_names_from_files():
    global boyNames, girlNames
    try:
        boyNames = open('boyNames.txt','U').read().strip().split('\n')
    except IOError:
        createBlankFile = open('boyNames.txt','a')
        createBlankFile.close()
        boyNames = []

    try:
        girlNames = open('girlNames.txt','U').read().strip().split('\n')
    except IOError:
        createBlankFile = open('girlNames.txt','a')
        createBlankFile.close()
        girlNames = []

def populate_name_dicts():
    import csv
    global YEAR_RANGE, STATE_UNRANKED, US_UNRANKED
    bnamedata = csv.reader(open('boyNameRanks%s.csv'%STATE,'rb'))
    gnamedata = csv.reader(open('girlNameRanks%s.csv'%STATE,'rb'))
    #bnamelist = [row for row in bnamedata]
    for row in list(bnamedata)[1:]:
        boyNameDict[row[0]] = RankedBabyName(*row)#, meaning = 'meaning')
    for row in list(gnamedata)[1:]:
        girlNameDict[row[0]] = RankedBabyName(*row)

    names = boyNameDict.values()
    names.extend(girlNameDict.values())
    yearMin = min([name.minYear for name in names])
    yearMax = max([name.maxYear for name in names])
    stateMax = max([name.stateMax for name in names])
    usMax = max([name.usMax for name in names])
    STATE_UNRANKED = stateMax+10
    US_UNRANKED = usMax+10
    YEAR_RANGE = range(yearMax,yearMin-1,-1) #decending order
    print 'Top',stateMax,'names in the state, and top',usMax,\
            'names in the US, for',yearMin,'to %d:'%yearMax
    print 'Loaded %d ranked boy\'s names.'%len(boyNameDict)
    print 'Loaded %d ranked girl\'s names.'%len(girlNameDict)

def print_name_lists_sorted():
    bUniquenesses = [(boyNameDict.get(n,noRank).uniqueness(),n)
                        for n in boyNames]
    bUniquenesses.sort(reverse = True)
    gUniquenesses = [(girlNameDict.get(n,noRank).uniqueness(),n)
                        for n in girlNames]
    gUniquenesses.sort(reverse = True)
    print '-'*20 + ' Our Boy Names (sorted by uniqueness) ' + '-'*21
    for (u,n) in bUniquenesses:
        if n != '':
            print boyNameDict.get(n, n + ' is not in top boy names.')
    print '-'*79
    print '-'*20 + ' Our Girl Names (sorted by uniqueness) ' + '-'*20
    for (u,n) in gUniquenesses:
        if n != '':
            print girlNameDict.get(n, n + ' is not in top girl names.')
    print '-'*79

def print_name_lists():
    print '-'*20 + ' Our Boy Names ' + '-'*44
    for n in boyNames:
        #print '-'*79
        if n != '':
            print boyNameDict.get(n, n + ' is not in top boy names.')
        #print boyNameDict.get(n, RankedBabyName(n,'boy')).rank_table()
    print '-'*79
    print '-'*20 + ' Our Girl Names ' + '-'*43
    for n in girlNames:
        #print '-'*79
        if n != '':
            print girlNameDict.get(n, n + ' is not in top girl names.')
        #print girlNameDict.get(n, RankedBabyName(n,'girl')).rank_table()
    print '-'*79

def rand_name():
    import random
    gender = random.choice(['boy','girl'])
    if gender == 'boy':
        rand_boy()
    else:
        rand_girl()

def rand_boy():
    import random
    boy_name_info(random.choice(boyNameDict.keys()))

def rand_girl():
    import random
    girl_name_info(random.choice(girlNameDict.keys()))

def boy_name_info(name_str):
    boy_inst = boyNameDict.get(name_str,noRank)
    print '-'*20 + ' Boy Name Info ' + '-'*44
    print boy_inst
    print boy_inst.rank_table()
    print '-'*79

def girl_name_info(name_str):
    girl_inst = girlNameDict.get(name_str,noRank)
    print '-'*20 + ' Girl Name Info ' + '-'*43
    print girl_inst
    print girl_inst.rank_table()
    print '-'*79

def baby_name_term():
    print('Enter "help", command, or "exit".')
    while True:
        input = raw_input('Namerizer> ')
        if input == 'exit':
            break
        elif input == 'help':
            print(HELP_MENU)
        elif input == 'names':
            print_name_lists()
        elif input == 'sorted':
            print_name_lists_sorted()
        elif input == 'rand':
            rand_name()
        elif input == 'boy':
            rand_boy()
        elif input == 'girl':
            rand_girl()
        elif input == 'reload':
            load_names_from_files()
        elif (input in boyNameDict.keys()) and (input in girlNameDict.keys()):
            boy_name_info(input)
            girl_name_info(input)
        elif input in boyNameDict.keys():
            boy_name_info(input)
        elif input in girlNameDict.keys():
            girl_name_info(input)
        elif input in boyNames:
            boy_name_info(input)
        elif input in girlNames:
            girl_name_info(input)
        elif input == '':
            pass
        else:
            try:
                exec('ans = ' + input)
                if ans is not None: print(ans)
            except SyntaxError:
                try:
                    exec(input)
                except BaseException as inst:
                    print(repr(inst))
                    print('Invalid command: ' + input)
            except BaseException as inst:
                print(repr(inst))
                print('Invalid command: ' + input)

boyNameDict = {}
girlNameDict = {}
load_names_from_files()

if __name__ == "__main__":
    populate_name_dicts()
    baby_name_term()
    