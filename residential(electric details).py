import requests
import urllib3
import re
import pymongo
from bs4 import BeautifulSoup
from pprint import pprint

myclient = pymongo.MongoClient('localhost',27017)
mydb = myclient.people
mycol = mydb.residential

class Information(object) :
    def __init__(self,main_info,list_of_plans,plans ):
        self.main_info = main_info
        self.list_of_plans = list_of_plans
        self.plans = plans

    def func(self):
        main_info = {}
        list_of_plans = []
        plans = {}

        url = "https://www.puc.nh.gov/ceps/shop.aspx"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        resident = soup.findAll('ul', {'class': 'dropdown-menu'})[0]
        for each_utility in resident.findAll('li'):
            for all_utilities in each_utility.findAll('a', href=True):
                for i in all_utilities:
                    main_url = 'https://www.puc.nh.gov/ceps/ResidentialCompare.aspx?choice={}'.format(i)
                    response = requests.get(main_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    content = soup.find('table', {'class': 'tblCompareList'})
                    for content in soup.findAll('table', {'class': 'tblCompareList'}):
                        plans = {'Plan_name': content.find('b', {'class': 'PlanName'}).get_text().strip(),
                            'Supplier_name': content.find('td', {'class': 'CompanyName'}).get_text().strip(),
                            'Description': content.find('td', {'colspan': '3', 'class': 'Comments'}).get_text().strip(),
                                    }
                        plans['Rate_last_updated'] = re.findall(r'\d+/\d+/\d+', str(content))
                        plans['Rate_last_updated'] = plans['Rate_last_updated'][0]
                        plans['Rate'] = re.findall(r'\d+\.\d+', str(content))
                        plans['Rate'] = plans['Rate'][1]
                        plans['Plan_term'] = re.findall(r'\d+', str(content))
                        plans['Plan_term'] = plans['Plan_term'][1]
                        plans['Renewable_energy'] = re.findall(r'\d+\.\d+.', str(content))
                        plans['Renewable_energy'] = plans['Renewable_energy'][2]
                        list_of_plans.append(plans)
            main_info[i] = list_of_plans
        print(main_info)
        mycol.insert_one(main_info)
all_req_data = Information('main_info','list_of_plans','plans')
all_req_data.func()
