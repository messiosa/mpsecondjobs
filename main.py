import pickle, os, spacy, time, datefinder, datetime, dateutil, re, urllib.parse, sys
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from dateutil.parser import parse
from tqdm import tqdm
from word2number import w2n

class Config:
    """
    date
        -> date to scrape ('yymmdd')

    selenium_path
        -> path to selenium Edge drivers

    categories_dict
    -> a dictionary which contains the categories used in The Register of Members' Financial Interests
        -> e.g. {'c1':'1. Employment and earnings'}
    """ 

    selenium_path = r"C:/selenium_drivers/edgedriver_win64_131"
    selenium_options = Options()
    selenium_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32")
    selenium_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    categories_dict = {
        'c1': '1. Employment and earnings',
        'c2a': '2. (a) Support linked to an MP but received by a local party organisation or indirectly via a central party organisation',
        'c2b': '2. (b) Any other support not included in Category 2(a)',
        'c3': '3. Gifts, benefits and hospitality from UK sources',
        'c4': '4. Visits outside the UK',
        'c5': '5. Gifts and benefits from sources outside the UK',
        'c6': '6. Land and property portfolio: (i) value over £100,000 and/or (ii) giving rental income of over £10,000 a year',
        'c7i': '7. (i) Shareholdings: over 15% of issued share capital',
        'c7ii': '7. (ii) Other shareholdings, valued at more than £70,000',
        'c8': '8. Miscellaneous',
        'c9': '9. Family members employed and paid from parliamentary expenses',
        'c10': '10. Family members engaged in lobbying the public sector on behalf of a third party or client'
    }

class Scrape:
    """
    The Scraper class contains the individual scrapers used to populate the MP class instances and create the final spreadsheets

    constituencies() -> None
        -> scrapes parliament.uk to create a pkl file which stores geography information
        -> creates ./pkl/dict_constituencies.pkl
        -> only needs to be run once (this information won't change)
        -> saved as a dictionary in the format: {'constituency1': ('region', 'country'), 'constituency2': ('region', 'country'), ...}
    
    links(date) -> None
        -> scrapes indexes from all web sources (parluk, pp, wiki, ipsa, db) to create a dict of all the individual mp urls needed
        -> creates ./pkl/dict_name_urls.pkl
        -> run it every time there's a new update on The Register (bi-weekly)
        -> saved as a dict with structure: {
                                            'mp1url':{'name': name,
                                                    'parlukurl': parlukurl,
                                                    'ppurl':ppurl,
                                                    'wikiurl':wikiurl,
                                                    'ipsaurl':ipsaurl,
                                                    'dburl':dburl
                                                    },
                                            'mp2url':{
                                                    ...
                                                    },
                                            ...
                                            }
    mpfi(mpurl) -> None:
        -> scrapes latest update of The Register once and stores it in a pkl to avoid repeat scraping
            -> if mpurl=None: runs for all mps
            -> if mpurl: only runs and updates for the individual mpurl
        -> creates ./pkl/dict_mpfi.pkl
        -> run it every time there's a new update on The Register (bi-weekly)
        -> pkl is structured according to category and with indent information (useful when parsing later)
        -> saved as a dict with structure: {
                                            'mp1url':{
                                                    '1. Employment and earnings': [('i','line'),('i2','line'), ...],
                                                    '4. Visits outside the UK': [('i','line'),('i2','line'), ...],
                                                    'x. ...': [(i,),(i,),(i,),...],
                                                    },
                                            'mp2url':{
                                                    ...
                                                    },
                                            ...
                                            }

    """

    def register_dates() -> None:
        os.environ['PATH'] = Config.selenium_path

        pages = ['https://publications.parliament.uk/pa/cm/cmregmem/contents2223.htm',
                'https://publications.parliament.uk/pa/cm/cmregmem/contents2122.htm',
                'https://publications.parliament.uk/pa/cm/cmregmem/contents1921.htm',
                'https://publications.parliament.uk/pa/cm/cmregmem/contents1920.htm']

        register_dates = []
        for page in pages:
            driver = webdriver.Edge(options=Config.selenium_options)
            driver.get(page)

            a_elements = driver.find_elements(By.TAG_NAME,'a')

            for a in a_elements:
                if a.text == 'HTML version':
                    date = a.get_attribute('href').split('https://publications.parliament.uk/pa/cm/cmregmem/')[1].split('/contents.htm')[0]
                    date_words = datetime.datetime.strftime(datetime.datetime.strptime(date,'%y%m%d'),'%d %B %Y')
                    register_dates.append((date,date_words))

        register_dates_file = open('./pkl/register_dates.pkl', 'wb')
        pickle.dump(register_dates, register_dates_file)

        return register_dates

    def constituencies() -> None: # Scrapes MP constituencies, works out regions and countries, and saves in pkl (dict_constituencies)
        os.environ['PATH'] = Config.selenium_path

        filter_list = ['Conservative','Labour','Green Party','Liberal Democrat',
            'Independent','Speaker','Plaid Cymru','Democratic Unionist Party',
            'Sinn Féin','Social Democratic & Labour Party','Alliance'] 
            ## need to filter out elements picked up by scraper which aren't constituencies

        dict_constituencies = {}

        # get england regions
        england_url = 'https://members.parliament.uk/region/Region/'
        england_regions = ['South East','West Midlands','North West','East Midlands','London',
        'Yorkshire and The Humber','East of England', 'South West', 'North East']

        for region in england_regions:
            driver = webdriver.Edge(options=Config.selenium_options) ## Slow, I know, but I get CAPTCHA'd if I don't open/close the browser every time
            driver.get(england_url+region)

            elements = driver.find_elements(By.CLASS_NAME,'primary-info')
            for item in elements:
                if item.text not in filter_list:
                    dict_constituencies[item.text] = (region,'England')        

            driver.close()

        #s,w,ni regions
        other_url = 'https://members.parliament.uk/region/Country/'
        other_regions = ['Scotland', 'Northern Ireland', 'Wales']

        for region in other_regions:
            driver = webdriver.Edge()
            driver.get(other_url+region)

            elements = driver.find_elements(By.CLASS_NAME,'primary-info')
            for item in elements:
                if item.text not in filter_list:
                    dict_constituencies[item.text] = (region,region)

            driver.close()
        
        # write dict_constituencies to pkl file
        dict_constituencies_file = open('./pkl/dict_constituencies.pkl', 'wb')
        pickle.dump(dict_constituencies, dict_constituencies_file)
        dict_constituencies_file.close()

    def links(date: str) -> None: # Scrapes urls for Register and parallelparliament, and saves in pkl (dict_name_urls)

        def parluk(date) -> dict: # -> {'mpurl':('name','parlukurl'), ...}
            url = 'https://publications.parliament.uk/pa/cm/cmregmem/'+date+'/contents.htm'
            os.environ['PATH'] = Config.selenium_path
            driver = webdriver.Edge(options=Config.selenium_options)

            driver.get(url)
            time.sleep(5)

            p_tags = driver.find_elements(By.TAG_NAME, 'p')

            # delete p's which are headers etc
            i = 0
            while i <= 7:
                del p_tags[0]
                i += 1
            time.sleep(5)

            # capture parlukurl / name in dict
            dict_parlukurl_name = {}
            for p_tag in tqdm(p_tags, desc="Parliament.uk"):
                a_tags = p_tag.find_elements(By.TAG_NAME, 'a')
                if len(a_tags) == 1:
                    parlukurl = a_tags[0].get_attribute('href')
                    name = a_tags[0].text.strip()
                if len(a_tags) == 2:
                    parlukurl = a_tags[1].get_attribute('href')
                    name = a_tags[1].text.strip()
                mpurl = urllib.parse.unquote(parlukurl.replace('https://publications.parliament.uk/pa/cm/cmregmem/'+date+'/','').replace('.htm',''))
                dict_parlukurl_name[mpurl] = (urllib.parse.unquote(name),urllib.parse.unquote(parlukurl))
            
            driver.close()

            return dict_parlukurl_name

        def pp(dict) -> dict: # -> {'mpurl':'ppurl', ...}
            dict_url_nameparlukurl = dict

            dict_ppurl = {}
            for mpurl in tqdm(dict_url_nameparlukurl.keys(), desc="ParallelParliament"):
                pp_url = str(mpurl.split('_')[1]+'-'+mpurl.split('_')[0])
                dict_ppurl[mpurl] = urllib.parse.unquote('https://www.parallelparliament.co.uk/mp/'+pp_url)
            
            dict_ppurl['dines_sarah'] = 'https://www.parallelparliament.co.uk/mp/miss-sarah-dines'
            dict_ppurl['qaisar_anum'] = 'https://www.parallelparliament.co.uk/mp/anum-qaisar-javed'
            dict_ppurl['davey_ed'] = 'https://www.parallelparliament.co.uk/mp/edward-davey'

            return dict_ppurl

        dict_url_nameparlukurl = parluk(date)
        dict_ppurl = pp(dict_url_nameparlukurl)

        failed_urls = []
        dict_name_urls = {}
        for mpurl, name_parlukurl in tqdm(list(dict_url_nameparlukurl.items()),desc="Compiling dict..."):
            try:
                name = name_parlukurl[0]
                parlukurl = urllib.parse.unquote(name_parlukurl[1])

                dict_name_urls[mpurl] = {
                    'name':name,
                    'parlukurl':parlukurl,
                    'ppurl':dict_ppurl[mpurl],
                }
                #print(mpurl,' SUCCESS')
            except Exception as e:
                failed_urls.append((mpurl,e))
                #print(mpurl,' FAILED')

        # save to pkl
        dict_name_urls_file = open('./pkl/'+date+'/dict_name_urls.pkl', 'wb')
        pickle.dump(dict_name_urls, dict_name_urls_file)
        dict_name_urls_file.close()

        return failed_urls

    def mpfi(mpurl: str = None) -> None: # Scrapes text from Register and saves in pkl (dict_mpfi)
            os.environ['PATH'] = Config.selenium_path
            dict_name_urls = pickle.load(open('./pkl/'+date+'/dict_name_urls.pkl','rb'))

            def get_indv_dict(parlukurl: str) -> dict:
                # option to add headers back in if I start getting blocked (False by default)
                driver = webdriver.Edge(options=Config.selenium_options) ## yes it's slow to open/close every time but otherwise you get CAPTCHA'd
                
                driver.get(parlukurl)

                content = driver.page_source
                soup = BeautifulSoup(content, 'html.parser')

                dict_indv_mpfi = {}
                all_text = soup.find('div', id='mainTextBlock').find_all('p')[1:]

                if all_text[0].text == 'Nil':
                    dict_indv_mpfi = None
                else:
                    for p in all_text:
                        if p.text in Config.categories_dict.values():
                            h = p.text
                            h_list = []
                        else:
                            try:
                                if p['class'][0] == 'indent':
                                    h_list.append(('i', p.text))
                                elif p['class'][0] == 'indent2':
                                    h_list.append(('i2', p.text))
                            except:
                                pass
                        dict_indv_mpfi[h] = h_list
                
                driver.close()

                return dict_indv_mpfi
            
            failed_urls = []
            if mpurl is None:
                dict_mpfi = {}
                for mpurl, name_urls in tqdm(dict_name_urls.items(), desc=mpurl):
                    parlukurl = name_urls['parlukurl']
                    try:
                        dict_indv_mpfi = get_indv_dict(parlukurl)
                        dict_mpfi[mpurl] = dict_indv_mpfi
                        #print(mpurl,' SUCCESS')
                    except Exception as e:
                        failed_urls.append((mpurl,e))
                        #print(mpurl,' FAIL')
            else:
                dict_mpfi = pickle.load(open('./pkl/'+date+'/dict_mpfi.pkl','rb'))
                parlukurl = dict_name_urls[mpurl]['parlukurl']
                dict_indv_mpfi = get_indv_dict(parlukurl)
                dict_mpfi[mpurl] = dict_indv_mpfi

            # save to pkl
            dict_mpfi_file = open('./pkl/'+date+'/dict_mpfi.pkl', 'wb')
            pickle.dump(dict_mpfi, dict_mpfi_file)
            dict_mpfi_file.close()

            return failed_urls

    def other_info(mpurl: str = None) -> None: # Scrapes Party and Constituency from ParallelParliament, and saves in pkl (dict_other_info)
            dict_name_urls = pickle.load(open('./pkl/'+date+'/dict_name_urls.pkl','rb'))
            dict_constituencies = pickle.load(open('./pkl/dict_constituencies.pkl','rb'))

            def get_indv_dict(mpurl):

                # SCRAPE PARALLELPARLIAMENT.CO.UK FOR PARTY
                def scrape_pp(ppurl: str):
                    os.environ['PATH'] = Config.selenium_path
                    driver = webdriver.Edge(options=Config.selenium_options)
                    driver.get(ppurl)
                
                    try:
                        party = driver.find_element(By.CLASS_NAME, 'card-header.text-center').find_element(By.TAG_NAME, 'h4').text.replace('\n','').split(' - ')[0].strip()
                    except Exception as e:
                        party = None
                    
                    try:
                        constituency = driver.find_element(By.CLASS_NAME, 'card-header.text-center').find_element(By.TAG_NAME, 'h4').text.replace('\n','').split(' - ')[1].strip()
                        if 'Former Member' in constituency:
                            constituency = None
                        region, country = dict_constituencies[constituency]
                    except Exception as e:
                        try:
                            constituency = driver.find_element(By.CLASS_NAME, 'card-header.text-center').find_element(By.TAG_NAME, 'h4').text
                            region, country = dict_constituencies[constituency]
                        except Exception as e:
                            constituency = None
                            region, country = None, None
                            #print('ppurl constituency failed:',e)
                    
                    driver.close()

                    return party, constituency, region, country

                ppurl = dict_name_urls[mpurl]['ppurl']
                party, constituency, region, country = scrape_pp(ppurl)

                dict_indv_mp = {
                    'name': dict_name_urls[mpurl]['name'],
                    'party': party,
                    'constituency': constituency,
                    'region': region,
                    'country': country,
                }

                return dict_indv_mp

            if mpurl == None:
                # if there is already a dict_other_info file then load that / else create a blank one
                if os.path.isfile('./pkl/'+date+'/dict_other_info.pkl'):
                    dict_other_info = pickle.load(open('./pkl/'+date+'/dict_other_info.pkl','rb'))
                    start_index = len(dict_other_info)-1 # repeats the last scraped mp in case the scrape was terminated part-way through
                else:
                    dict_other_info = {}
                    start_index = 0
                    dict_other_info_file = open('./pkl/'+date+'/dict_other_info.pkl', 'wb')
                    pickle.dump(dict_other_info, dict_other_info_file)
                    dict_other_info_file.close()
                
                failed_urls = []
                for mpurl, name_urls in tqdm(list(dict_name_urls.items())[start_index:]):
                    try:
                        dict_other_info = pickle.load(open('./pkl/'+date+'/dict_other_info.pkl','rb'))
                        dict_other_info[mpurl] = get_indv_dict(mpurl) # not very efficient to open/close but this allows for doing this scrape in bursts as it takes a long time (~3-4 hours)

                        dict_other_info_file = open('./pkl/'+date+'/dict_other_info.pkl', 'wb')
                        pickle.dump(dict_other_info, dict_other_info_file)
                        dict_other_info_file.close()
                    except Exception as e:
                        #print('*** FAILED ***',mpurl,e)
                        failed_urls.append((mpurl,e))
                
                # MANUAL ADD-INS
                try:
                    dict_other_info['mortimer_jill']['party'] = 'Conservative'
                    dict_other_info['mortimer_jill']['constituency'] = 'Hartlepool'
                    dict_other_info['mortimer_jill']['region'], dict_other_info['mortimer_jill']['country'] = dict_constituencies[dict_other_info['mortimer_jill']['constituency']]
                except:
                    pass
                try:
                    dict_other_info['wilson_sammy']['party'] = 'Democratic Unionist Party'
                    dict_other_info['wilson_sammy']['constituency'] = 'East Antrim'
                    dict_other_info['wilson_sammy']['region'], dict_other_info['wilson_sammy']['country'] = dict_constituencies[dict_other_info['wilson_sammy']['constituency']]
                except:
                    pass
                try:
                    dict_other_info['leadbeater_kim']['party'] = 'Labour'
                    dict_other_info['leadbeater_kim']['constituency'] = 'Batley and Spen'
                    dict_other_info['leadbeater_kim']['region'], dict_other_info['leadbeater_kim']['country'] = dict_constituencies[dict_other_info['leadbeater_kim']['constituency']]
                except:
                    pass
                try:
                    dict_other_info['green_sarah']['party'] = 'Liberal Democrat'
                    dict_other_info['green_sarah']['constituency'] = 'Chesham and Amersham'
                    dict_other_info['green_sarah']['region'], dict_other_info['green_sarah']['country'] = dict_constituencies[dict_other_info['green_sarah']['constituency']]
                except:
                    pass

                # double-check everything was scraped correctly (sometimes it doesn't always pick everything up - maybe the connection dropped during scraping etc.)
                for mpurl, other_info in dict_other_info.items():
                    if None in other_info.values():
                        try:
                            dict_other_info[mpurl] = get_indv_dict(mpurl)
                        except:
                            pass
                
                list_name_urls = [mpurl for mpurl, name_urls in dict_name_urls.items()]
                list_other_info = [mpurl for mpurl, other_info in dict_other_info.items()]

                missing_mp_list = set(list_name_urls)-set(list_other_info)

                for mp in missing_mp_list:
                    dict_other_info[mp] = get_indv_dict(mp)

                # SAVE TO PKL
                dict_other_info_file = open('./pkl/'+date+'/dict_other_info.pkl', 'wb')
                pickle.dump(dict_other_info, dict_other_info_file)
                dict_other_info_file.close()

                #print('\n\n*** FAILED URLS ***\n\n',failed_urls,'\n\n *** \n\n')

            else:
                dict_other_info = pickle.load(open('./pkl/'+date+'/dict_other_info.pkl','rb'))
                try:
                    dict_other_info[mpurl] = get_indv_dict(mpurl)
                except Exception as e:
                    #print('get_indv_mp failed:',e)
                    pass

                dict_other_info_file = open('./pkl/'+date+'/dict_other_info.pkl', 'wb')
                pickle.dump(dict_other_info, dict_other_info_file)
                dict_other_info_file.close()

class Extract:
    """
    The Extract class contains the functions required to turn dict_mpfi into the final data needed
    for the spreadsheet. It uses custom-built named entity recognition models (spaCy) to extract entities.

    mpfi() -> None
        -> This function turns the lines stored in dict_mpfi into a long list of dicts where each dict represents a line. 
        -> The dict contains all of the final data required for the spreadsheet and is structured like this: 
            [
                {
                    'name': 'Abbott, Ms Diane', 
                    'full_text': 'Payments from the Guardian, Kings Place, 90 York Way, London N1 9GU, for articles:', 
                    'parlukurl': 'https://publications.parliament.uk/pa/cm/cmregmem/220419/abbott_diane.htm', 
                    'date': '', 'orgs': 'the Guardian', 
                    'money': '', 'time': '', 
                    'role': 'for articles', 
                    'total_money_ytd': None, 
                    'total_time_ytd': None
                },
                {
                    ...
                },
                ...
            ]
    
    """

    def date_processor(dict_line: str) -> datetime: #dict_line['date'] -> start_date_ytd, end_date_ytd

        def ytd(date: datetime) -> datetime: # date -> date_ytd
            if date <= mpfi_date_minus_one_year:
                date_ytd = mpfi_date_minus_one_year
            elif date >= mpfi_date_minus_one_year and date <= mpfi_date:
                date_ytd = date
            elif date >= mpfi_date:
                date_ytd = mpfi_date
            
            return date_ytd

        date_raw = dict_line['date']

        # filter out any date lists with more than 1 element / choose longest date / make lowercase for processing
        if len(date_raw) > 1: date_raw = max(date_raw, key=len).lower()     # takes longest item in dict_date as new dict_date                    
        else: date_raw = date_raw[0].lower()

        date_raw = date_raw.replace('further notice',date_words).replace('election to parliament',election_date_words)

        # datefinder is very buggy - it works best if I take out keywords such as from and until and replace them with hashes
        date_keywords = ['from','since','onwards','until','between',' and ',' to ']

        datefinder_raw = date_raw
        for keyword in date_keywords:
            if keyword in datefinder_raw:
                datefinder_raw = datefinder_raw.replace(keyword,'#')

        dates = [i for i in datefinder.find_dates(datefinder_raw)]
        # get start_date and end_date
        if len(dates) == 2:
            start_date = ytd(dates[0])
            end_date = ytd(dates[1])

        elif len(dates) == 1:
            if any([i for i in ['from','since','onwards'] if i in date_raw]):
                start_date = ytd(dates[0])
                end_date = mpfi_date
            elif 'until' in date_raw:
                end_date = ytd(dates[0])
                start_date = ytd(end_date+datetime.timedelta(-365))
            else:
                start_date = ytd(dates[0])
                end_date = ytd(dates[0])

        return start_date, end_date

    def total_money_ytd(dict_line: str) -> int: ## dict_line => total_money_ytd
        # if date or money is missing, return none
        if len(dict_line['date']) == 0:
            total_money_ytd = float(0)
        elif len(dict_line['money']) == 0:
            total_money_ytd = float(0)
        else:
            # for dict_line['total_money_ytd']: find money_period and money_raw_value
            period_dict = {
                '1': 1,
                'D': 365,
                'W': 52,
                '2W': 26,
                'M': 12,
                'Q': 4,
                'Y': 1,
                'NA': 1
            }
            if len(dict_line['money']) > 1:
                total_money_ytd = 'MANUAL_CHECK'
                print('#1')
            else:
                try:
                    money_raw_value = float(''.join([i for i in dict_line['money'][0] if i.isdigit() is True or i == '.']))
                except:
                    total_money_ytd = 'MANUAL_CHECK'
                    print('#2')
                    return total_money_ytd
                money_period = nlp_money(dict_line['money'][0]).ents[0].label_

                # for dict_line['total_money_ytd']: calculate total_money_ytd
                if money_period == '1':                                         # for non-recurring sums, check if the sum is in date
                    try:
                        date_parsed = dateutil.parser.parse(dict_line['date'][0])
                        if date_parsed < mpfi_date_minus_one_year:
                            total_money_ytd = float(0)
                        else:
                            total_money_ytd = float(money_raw_value)
                    except:
                        start_date_ytd, end_date_ytd = Extract.date_processor(dict_line)
                        total_money_for_one_year = money_raw_value*period_dict[money_period]
                        try:
                            percentage_of_year_elapsed = (end_date_ytd-start_date_ytd).days/365
                            if percentage_of_year_elapsed == 0.0:                    # for a single date, start_date_ytd = end_date_ytd and percentage_.. = 0
                                total_money_ytd = float(0)
                            else:
                                total_money_ytd = float(round(total_money_for_one_year*percentage_of_year_elapsed))
                        except:                                                       # if date_processor returns None's
                            total_money_ytd = 'MANUAL_CHECK'
                            print('#3')
                else:                                                                 # for recurring sums (i.e. D, W, 2W, M, Q, Y)
                    start_date_ytd, end_date_ytd = Extract.date_processor(dict_line)
                    total_money_for_one_year = money_raw_value*period_dict[money_period]
                    try:
                        percentage_of_year_elapsed = (end_date_ytd-start_date_ytd).days/365
                        if percentage_of_year_elapsed == 0.0:                         # for a single date, start_date_ytd = end_date_ytd and percentage_.. = 0
                            total_money_ytd = float(0)
                        else:
                            total_money_ytd = float(round(total_money_for_one_year*percentage_of_year_elapsed))
                    except:                                                          # if date_processor returns None's
                        total_money_ytd = float(0)

        # try:
        #     if total_money_ytd > 500000:
        #         total_money_ytd = 'MANUAL_CHECK'
        #         print('#4')
        #     else:
        #         pass
        # except:
        #     pass

        return total_money_ytd         
    
    def total_time_ytd(dict_line: str) -> int: ## dict_line => total_money_ytd

        ##################################
        ## TOTAL_TIME_YTD SUB-FUNCTIONS ##
        ##################################

        def numwords(text):
            list_text = text.split(' ')
            #print(list_text)
            list_new_text = []
            for item in list_text:
                try:
                    list_new_text.append(w2n.word_to_num(item))
                except:
                    list_new_text.append(item)
            #print(list_new_text)

            new_text = ' '.join([str(item) for item in list_new_text])
            
            if 'a year' in new_text:                                                    
                new_text = new_text.replace('a year', 'per year')       # nlp_trf doesn't like 'a year' for some reason...
            #print(new_text)
            return new_text

        def time_processor(text): # dict_line['time'] > time_raw_value
            
            # replace any word-nums with nums
            text = numwords(text)
            #print(text)

            # extract date and remove 'per month' etc
            doc_time = nlp_trf(text)
            try:                                                                       
                time = [i for i in doc_time.ents if i.label_ == 'TIME'][0].text
            except:
                try:                                                                    # times given in days (e.g. '8 days per month') are recognised as 'DATE' ents by nlp_trf
                    time = [i for i in doc_time.ents if i.label_ == 'DATE'][0].text
                except:                                     
                    time = float(0)
                    return time

            # REMOVE MISLEADING WORDS
            time = time.replace('non-consecutive','')

            # PROCESS FOR RANGES
            if '-' in time:
                time_raw_value = time.rsplit('-')[1].strip() #strip out hyphens (and non-numerics) and use higher bound figure (e.g. 80-100 hours)
            elif ' and ' in time:
                time_raw_value = time.rsplit(' and ')[1].strip() #strip out ' and ' (and non-numerics) and use higher bound figure (e.g. 80 and 100 hours)
            elif 'approx.' in time:
                time_raw_value = time.replace('approx.','')[1].strip() #strip out 'approx' (and non-numerics) and use higher bound figure (e.g. 80-100 hours)
            else:
                time_raw_value = time
            
            # PROCESS FOR MINS/HOURS
            m_keywords = ['mins','min']
            h_keywords = ['hrs','hours','hr']
            d_keywords = ['day']

            list_mhd = []
            for item in m_keywords:
                if item in time_raw_value: list_mhd.append('m')
            for item in h_keywords:
                if item in time_raw_value: list_mhd.append('h')  
            for item in d_keywords:
                if item in time_raw_value: list_mhd.append('d')  

            if 'm' in list_mhd and 'h' in list_mhd:
                list_time_values = [float(s) for s in re.findall(r'-?\d+\.?\d*', time_raw_value)]
                hrs = list_time_values[0]
                mins = list_time_values[1]
            elif 'h' in list_mhd and 'm' not in list_mhd:
                try:
                    hrs = float(re.findall(r'-?\d+\.?\d*', time_raw_value)[0])
                except:                                                         # PROCESS FOR WORD-NUMBERS (E.G.'SIX HOURS')
                    pass
                mins = float(0)
            elif 'm' in list_mhd and 'h' not in list_mhd:
                try: 
                    mins = float(re.findall(r'-?\d+\.?\d*', time_raw_value)[0])
                except:                                                         # PROCESS FOR WORD-NUMBERS (E.G.'THIRTY MINUTES')
                    pass
                hrs = float(0)
            elif 'd' in list_mhd:
                days = float(re.findall(r'-?\d+\.?\d*', time_raw_value)[0])
                hrs = days*8                                                     # ASSUMING 8-HOUR WORKING DAY
                mins = float(0)                                                 

            time_raw_value = round(hrs+(mins/60), 2)                             # TIME_RAW_VALUE IN HOURS

            return time_raw_value

        ##################################
        ## TOTAL_TIME_YTD MAIN FUNCTION ##
        ##################################

        # if date or money is missing, return none
        if len(dict_line['date']) == 0:
            total_time_ytd = float(0)
        elif len(dict_line['time']) == 0:
            total_time_ytd = float(0)
        else:
            # for dict_line['total_money_ytd']: find money_period and money_raw_value
            period_dict = {
                '1': 1,
                'D': 365,
                'W': 52,
                '2W': 26,
                'M': 12,
                'Q': 4,
                'Y': 1,
                'NA': 1
            }
            if len(dict_line['time']) > 1:
                total_time_ytd = 'MANUAL_CHECK'
            else:
                time_raw_value = time_processor(dict_line['time'][0])
                if time_raw_value == 'MANUAL_CHECK':
                    total_time_ytd = 'MANUAL_CHECK'
                    return total_time_ytd
                time_period = nlp_time(dict_line['time'][0]).ents[0].label_

                # for dict_line['total_money_ytd']: calculate total_money_ytd
                if time_period == '1':                                         # for non-recurring sums, check if the sum is in date
                    try:
                        date_parsed = [i for i in datefinder.find_dates(dict_line['date'][0])][0]
                        if date_parsed < mpfi_date_minus_one_year:
                            total_time_ytd = float(0)
                        else:
                            total_time_ytd = float(time_raw_value)
                    except:
                        start_date_ytd, end_date_ytd = Extract.date_processor(dict_line)
                        total_time_for_one_year = time_raw_value*period_dict[time_period]
                        try:
                            percentage_of_year_elapsed = (end_date_ytd-start_date_ytd).days/365
                            if percentage_of_year_elapsed == 0.0:                    # for a single date, start_date_ytd = end_date_ytd and percentage_.. = 0
                                total_time_ytd = float(0)
                            else:
                                total_time_ytd = float(round(total_time_for_one_year*percentage_of_year_elapsed, 2))
                        except:                                                       # if date_processor returns None's
                            total_time_ytd = float(0)
                else:                                                                 # for recurring sums (i.e. D, W, 2W, M, Q, Y)
                    start_date_ytd, end_date_ytd = Extract.date_processor(dict_line)
                    total_time_for_one_year = time_raw_value*period_dict[time_period]
                    try:
                        percentage_of_year_elapsed = (end_date_ytd-start_date_ytd).days/365
                        if percentage_of_year_elapsed == 0.0:                         # for a single date, start_date_ytd = end_date_ytd and percentage_.. = 0
                            total_time_ytd = float(0)
                        else:
                            total_time_ytd = float(round(total_time_for_one_year*percentage_of_year_elapsed, 2))
                    except:                                                          # if date_processor returns None's
                        total_time_ytd = float(0)

        return total_time_ytd  

    def parse_lines_mp(mpurl: str, category: str = 'c1') -> list: ## mpurl => parsed_lines_mp
        dict_name_urls = pickle.load(open('./pkl/'+date+'/dict_name_urls.pkl','rb'))
        dict_mpfi = pickle.load(open('./pkl/'+date+'/dict_mpfi.pkl','rb'))
        
        mpfi = dict_mpfi[mpurl]
        cat = Config.categories_dict[category]

        """
        try to unpack lines (('i','line'),...) from dict_mpfi into list_lines 
        but if there are no lines then just return a list with the below dict as the only dict
        """

        try:
            mpfi_lines = mpfi[cat]
        except Exception as e:
            parsed_lines_mp = [{
                            'name':dict_name_urls[mpurl]['name'],
                            'full_text':None,
                            'date':None,
                            'orgs':None,
                            'money':None,
                            'time':None,
                            'role':None,
                            'total_money_ytd':None,
                            'total_time_ytd':None,
                            'parlukurl':dict_name_urls[mpurl]['parlukurl'],
                            'register_date':datetime.datetime.strptime(date_words,"%d %B %Y")
                            }]
            
            try:
                dict_parsed_lines_all = pickle.load(open('./pkl/'+date+'/dict_parsed_lines.pkl','rb'))
                dict_parsed_lines_all[mpurl] = parsed_lines_mp
            except Exception as e:
                dict_parsed_lines_all = {}
                dict_parsed_lines_all[mpurl] = parsed_lines_mp

            dict_parsed_lines_file = open('./pkl/'+date+'/dict_parsed_lines.pkl', 'wb')
            pickle.dump(dict_parsed_lines_all, dict_parsed_lines_file)
            dict_parsed_lines_file.close()    
            
            return parsed_lines_mp

        parsed_lines_mp = []
        i_list = []
        for line in mpfi_lines:
            try:
                indent = line[0]
                full_text = line[1]

                dict_line = {}
                doc = nlp_all_ents(full_text)
                dict_line['name'] = dict_name_urls[mpurl]['name']
                dict_line['full_text'] = full_text
                dict_line['parlukurl'] = dict_name_urls[mpurl]['parlukurl']
                dict_line['date'] = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
                dict_line['orgs'] = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
                dict_line['money'] = [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
                dict_line['time'] = [ent.text for ent in doc.ents if ent.label_ == 'TIME']
                dict_line['role'] = [ent.text for ent in doc.ents if ent.label_ == 'ROLE']

                money_ytd = Extract.total_money_ytd(dict_line)
                time_ytd = Extract.total_time_ytd(dict_line)

                if money_ytd == 'MANUAL_CHECK' or time_ytd == 'MANUAL_CHECK':
                    print('money_ytd:',money_ytd)
                    print('time_ytd:',time_ytd)

                    print('\n')
                    print('MANUAL CHECK:')
                    print(dict_line['full_text'],'\n')
                    new_date = input('Enter correct date: ')
                    print('\n')
                    new_money = input('Enter correct sum: ')
                    print('\n')
                    new_time = input('Enter correct time: ')
                    print('\n')

                    dict_line['date'] = [new_date]
                    dict_line['money'] = [new_money]
                    dict_line['time'] = [new_time]

                    money_ytd = Extract.total_money_ytd(dict_line)
                    print('money_ytd:',money_ytd)
                    time_ytd = Extract.total_time_ytd(dict_line)
                    print('time_ytd:',time_ytd)

                dict_line['total_money_ytd'] = float(money_ytd)
                dict_line['total_time_ytd'] = float(time_ytd)

                if indent == 'i':
                    i_fulltext = dict_line['full_text']
                    i_orgs = dict_line['orgs']
                    i_role = dict_line['role']
                    i_list.append('i')

                if indent == 'i2':
                    dict_line['full_text'] = i_fulltext+dict_line['full_text']
                    dict_line['orgs'] = i_orgs+dict_line['orgs']
                    dict_line['role'] = i_role+dict_line['role']
                    i_list.append('i2')

                # formatting date and money fields back to strings (from lists) to export to DataFrame
                dict_line['orgs'] = str(', '.join(dict_line['orgs']))
                dict_line['date'] = str(', '.join(dict_line['date']))
                dict_line['money'] = str(', '.join(dict_line['money']))
                dict_line['time'] = str(', '.join(dict_line['time']))
                dict_line['role'] = str(', '.join(dict_line['role']))

                # add Register date
                dict_line['register_date'] = datetime.datetime.strptime(date_words,"%d %B %Y").date()

                # finally, append dict_line to list_mpdata
                parsed_lines_mp.append(dict_line)
            except Exception as e:
                print('FAILED LINE: ')
                print(line)
                print(e,'\n')
        try:
            dict_parsed_lines_all = pickle.load(open('./pkl/'+date+'/dict_parsed_lines.pkl','rb'))
            dict_parsed_lines_all[mpurl] = parsed_lines_mp
        except Exception as e:
            dict_parsed_lines_all = {}
            dict_parsed_lines_all[mpurl] = parsed_lines_mp

        dict_parsed_lines_file = open('./pkl/'+date+'/dict_parsed_lines.pkl', 'wb')
        pickle.dump(dict_parsed_lines_all, dict_parsed_lines_file)
        dict_parsed_lines_file.close()    

    def parse_lines_all(category: str = 'c1') -> None:
        # dicts
        dict_mpfi = pickle.load(open('./pkl/'+date+'/dict_mpfi.pkl','rb'))

        # main logic - if no mpurl is entered then all mpurls in dict_mpfi will be processed
        failed_urls = []
        for mpurl, mpfi in dict_mpfi.items():
            try:
                Extract.parse_lines_mp(mpurl, category)
                #print(mpurl,' SUCCESS')
            except Exception as e:
                failed_urls.append((mpurl,e))
                #print(mpurl,' FAIL')

        return failed_urls

    def manual(mpurl: str, category: str = 'c1') -> None:
        dict_name_urls = pickle.load(open('./pkl/'+date+'/dict_name_urls.pkl','rb'))
        dict_mpfi = pickle.load(open('./pkl/'+date+'/dict_mpfi.pkl'))

        mpfi = dict_mpfi[mpurl]
        cat = Config.categories_dict[category]

        try:
            mpfi_lines = mpfi[cat]
        except Exception as e:
            parsed_lines_mp = [{
                            'name':str(dict_name_urls[mpurl]['name']),
                            'full_text':None,
                            'date':None,
                            'orgs':None,
                            'money':None,
                            'time':None,
                            'role':None,
                            'total_money_ytd':None,
                            'total_time_ytd':None,
                            'parlukurl':str(dict_name_urls[mpurl]['parlukurl'])
                            }]
            #print(mpurl,e)
            return parsed_lines_mp
        
        parsed_lines_mp = []
        failed_lines = []
        i_list = []
        for line in mpfi_lines:
            try:
                indent = line[0]
                full_text = line[1]

                #print('\n')
                #print('line: ',line)
                dict_line = {}
                doc = nlp_all_ents(full_text)
                dict_line['name'] = dict_name_urls[mpurl]['name']
                dict_line['full_text'] = full_text
                dict_line['parlukurl'] = dict_name_urls[mpurl]['parlukurl']
                dict_line['date'] = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
                dict_line['orgs'] = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
                dict_line['money'] = [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
                dict_line['time'] = [ent.text for ent in doc.ents if ent.label_ == 'TIME']
                dict_line['role'] = [ent.text for ent in doc.ents if ent.label_ == 'ROLE']

                #print(dict_line)

                total_money_ytd = Extract.total_money_ytd(dict_line)
                total_time_ytd = Extract.total_time_ytd(dict_line)

                dict_line['total_money_ytd'] = float(total_money_ytd)
                dict_line['total_time_ytd'] = float(total_time_ytd)

                if indent == 'i':
                    i_fulltext = dict_line['full_text']
                    i_orgs = dict_line['orgs']
                    i_role = dict_line['role']
                    i_list.append('i')

                if indent == 'i2':
                    dict_line['full_text'] = i_fulltext+dict_line['full_text']
                    dict_line['orgs'] = i_orgs+dict_line['orgs']
                    dict_line['role'] = i_role+dict_line['role']
                    i_list.append('i2')

                # formatting date and money fields back to strings (from lists) to export to DataFrame
                dict_line['orgs'] = str(', '.join(dict_line['orgs']))
                dict_line['date'] = str(', '.join(dict_line['date']))
                dict_line['money'] = str(', '.join(dict_line['money']))  
                dict_line['time'] = str(', '.join(dict_line['time']))
                dict_line['role'] = str(', '.join(dict_line['role']))

                # finally, append dict_line to list_mpdata
                parsed_lines_mp.append(dict_line)

            except Exception as e:
                failed_lines.append(line)
        
        for line in failed_lines:
            #print('\n',line,'\n')

            input_org = input('Enter organizations:').split('#')
            input_money = input('Enter money:').split('#')
            input_time = input('Enter hours:').split('#')
            input_date = input('Enter dates:').split('#')
            input_role = input('Enter roles:').split('#')

            dict_line = {}
            dict_line['name'] = dict_name_urls[mpurl]['name']
            dict_line['full_text'] = [line]
            dict_line['parlukurl'] = dict_name_urls[mpurl]['parlukurl']
            dict_line['date'] = input_date
            dict_line['orgs'] = input_org
            dict_line['money'] = input_money
            dict_line['time'] = input_time
            dict_line['role'] = input_role

            total_money_ytd = Extract.total_money_ytd(dict_line)
            total_time_ytd = Extract.total_time_ytd(dict_line)

            dict_line['total_money_ytd'] = float(total_money_ytd)
            dict_line['total_time_ytd'] = float(total_time_ytd)

            if indent == 'i':
                i_fulltext = dict_line['full_text']
                i_orgs = dict_line['orgs']
                i_role = dict_line['role']
                i_list.append('i')
            
            if indent == 'i2':
                dict_line['full_text'] = i_fulltext+dict_line['full_text']
                dict_line['orgs'] = i_orgs+dict_line['orgs']
                dict_line['role'] = i_role+dict_line['role']
                i_list.append('i2')
            
            # formatting date and money fields back to strings (from lists) to export to DataFrame
            dict_line['orgs'] = str(', '.join(dict_line['orgs']))
            dict_line['date'] = str(', '.join(dict_line['date']))
            dict_line['money'] = str(', '.join(dict_line['money']))  
            dict_line['time'] = str(', '.join(dict_line['time']))
            dict_line['role'] = str(', '.join(dict_line['role']))

            parsed_lines_mp.append(dict_line)
        
        parsed_lines_all = pickle.load(open('./pkl/'+date+'/dict_parsed_lines.pkl','rb'))
        if mpurl in parsed_lines_all.keys():
            del parsed_lines_all[mpurl]
        parsed_lines_all[mpurl] = parsed_lines_mp

        parsed_lines_file = open('./pkl/'+date+'/dict_parsed_lines.pkl', 'wb')
        pickle.dump(parsed_lines_all, parsed_lines_file)
        parsed_lines_file.close()

        # return failed_lines if wanted for additional NER training
        return failed_lines

class Export:
    """
    The Export class contains the functions used to turn parsed_lines into pandas DataFrames.
    """    

    def df(date) -> pd.DataFrame:
        dict_other_info = pickle.load(open('./pkl/'+date+'/dict_other_info.pkl','rb'))
        dict_parsed_lines = pickle.load(open('./pkl/'+date+'/dict_parsed_lines.pkl','rb'))

        # SHEET 1 - MP OVERVIEW
        df_other_info = pd.DataFrame(dict_other_info).transpose()

        # Calculate sum_money_ytd and sum_time_ytd for MP Overview sheet and then add to dict_sum_moneytime { 'mpurl':{'sum_money_ytd':VALUE, 'sum_time_ytd':VALUE}, ...
        dict_sum_moneytime = {}
        for mpurl, parsed_lines in tqdm(dict_parsed_lines.items(), desc="Calculating Total £/hours"):
            list_total_money_ytd = []
            list_total_time_ytd = []
            for line in parsed_lines:
                list_total_money_ytd.append(line['total_money_ytd'])
                list_total_time_ytd.append(line['total_time_ytd'])
            dict_sum_moneytime[mpurl] = {
                'sum_money_ytd': sum([i for i in list_total_money_ytd if type(i) is float or type(i) is int]),
                'sum_time_ytd': sum([i for i in list_total_time_ytd if type(i) is float or type(i) is int])
            }

        df_sum_moneytime = pd.DataFrame(dict_sum_moneytime).transpose()

        df_mp_overview = pd.concat([df_sum_moneytime, df_other_info], axis=1)
        df_mp_overview = df_mp_overview[["name","party","constituency","sum_money_ytd","sum_time_ytd","region","country"]]
        df_mp_overview = df_mp_overview.rename(columns = {
            'name':'Name',
            'party':'Political Party',
            'constituency':'Constituency',
            'sum_money_ytd':'Secondary Earnings YTD (£)',
            'sum_time_ytd': 'Secondary Hours Worked YTD',
            'region':'Region',
            'country':'Country',
        })
        #df_mp_overview = df_mp_overview.set_index('Name')
        #df_mp_overview = df_mp_overview.sort_index(ascending=True)
        #df_mp_overview = df_mp_overview.fillna(0)

        # SHEET 2 - EARNINGS BREAKDOWN - create df from list_lines and re-name columns
        list_lines = []
        for mplist in tqdm(list(dict_parsed_lines.values()), desc="Adding parsed lines to DataFrame"):
            for line in mplist:
                list_lines.append(line)    

        df_mpfi = pd.DataFrame(list_lines)
        df_second_jobs = df_mpfi[["name","orgs","role","money","time","date","total_money_ytd","total_time_ytd","parlukurl"]]
        df_second_jobs = df_second_jobs.rename(columns={
            'name':'Name',
            'money':'Earnings (RAW)',
            'time':'Hours worked (RAW)',
            'date':'Date of Earnings',
            'orgs':'Client/Organisation',
            'role':'Role',
            'total_money_ytd':'Earnings YTD (£)',
            'total_time_ytd':'Hours worked YTD',
            'parlukurl':'Source'
        })
        #df_second_jobs = df_second_jobs.set_index('Name')
        #df_second_jobs = df_second_jobs.sort_index(ascending=True)
        #df_second_jobs = df_second_jobs.fillna(0)

        return df_mp_overview, df_second_jobs

    def df_mega():
        # Create list of directory names (which will turn into dates)
        dir_list = [i for i in os.listdir('./pkl') if i not in ['dict_constituencies.pkl','register_dates.pkl']]

        # Create empty 'mega' dataframes which will incorporate data from all dates
        df_mp_overview_mega = pd.DataFrame({})
        df_second_jobs_mega = pd.DataFrame({})

        # loop through list of dirs/dates and: 1) create a df for each, 2) append a 'Register date' column with the register entry date, 3) append df to df_mega
        for dir in dir_list:
            df_mp_overview, df_second_jobs = Export.df(dir)
            df_mp_overview['Register date'] = datetime.datetime.strptime(dir,'%y%m%d').date()
            df_second_jobs['Register date'] = datetime.datetime.strptime(dir,'%y%m%d').date()
            df_mp_overview_mega = pd.concat([df_mp_overview_mega,df_mp_overview])
            df_second_jobs_mega = pd.concat([df_second_jobs_mega,df_second_jobs])
        
        return df_mp_overview_mega, df_second_jobs_mega

# exec
if __name__ == "__main__":
    # variables
    print('loading dates...')
    date = sys.argv[1]
    date_words = sys.argv[2]
    print('date: ',date,' / date_words: ',date_words)
    election_date = '191212'
    election_date_words = '12 December 19'
    mpfi_date = dateutil.parser.parse(date, yearfirst=True)
    mpfi_date_minus_one_year = mpfi_date+datetime.timedelta(-365)

    # Create pkl folder for date
    if os.path.exists('./pkl/'+date):
        pass
    else:
        os.mkdir('./pkl/'+date)

    # Full scrape (i.e., run Scrape.other_info() too?)
    print('Scraping links...')
    failed_urls_links = Scrape.links(date)
    print('Scraping other info...')
    Scrape.other_info()

    # spaCy models
    print('loading spaCy models...')
    nlp_trf = spacy.load('en_core_web_trf')
    nlp_time = spacy.load('./ner_models/time/model-best/')
    nlp_money = spacy.load("./ner_models/money/model-best")
    nlp_all_ents = spacy.load("./ner_models/all_ents/model-best")

    # print('Scraping MPFI...')
    failed_urls_mpfi = Scrape.mpfi()

    print('Extracting...')
    failed_urls_parse = Extract.parse_lines_all()

    print('Exporting...')
    df_mp_overview_mega, df_second_jobs_mega = Export.df_mega()
    df_mp_overview_mega.to_pickle('df_mp_overview_mega.pkl')
    df_second_jobs_mega.to_pickle('df_second_jobs_mega.pkl')
    df_mp_overview, df_second_jobs = Export.df(date)
    df_mp_overview.to_pickle('df_mp_overview.pkl')
    df_second_jobs.to_pickle('df_second_jobs.pkl')
    with open('latest_scrape_date.txt','w') as f:
        f.write(date)

    print('\n','*********************************')
    print('failed_urls_links: ',failed_urls_links)
    print('failed_urls_mpfi: ',failed_urls_mpfi)
    print('failed_urls_parse: ',failed_urls_parse)