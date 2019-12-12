import requests
import csv
from colorama import init, Fore, Style
import traceback
import os
from requests.exceptions import TooManyRedirects


# Function for reading data from csv file. First argument is name of CSV file and the second is domain.
# When you read URL path from CSV you are adding domain to the beginning
# Function return dictionary which contains Tested URL and Expected URL
def read_csv(file_name, domain):
    print("Reading information from file ...")
    data_list = []
    base_urls = []
    expected_urls = []
    with open(f'{file_name}', 'r', encoding="utf-8") as file:
        data = csv.DictReader(file)
        for row in data:
            base_urls.append(domain + row['Test URL'])
            expected_urls.append(domain + row['Expected URL'])
    data_list.append({
        'base_urls': base_urls,
        'expected_urls': expected_urls
    })
    print("Reading is finished")
    return data_list


# Function for checking link redirects
# Function takes 2 arguments: 1) list of Tested URLs; 2) list of Expected URLs
# Function return
def check_redirects(base_url, expected_url):
    print("Start checking ...")
    correct_links = 0
    incorrect_links = 0
    same_page = 0
    result = []
    count = 1
    for b_url, exp_url in zip(base_url, expected_url):
        try:
            if b_url == exp_url:
                pass
            else:
                r = requests.Session()
                r.max_redirects = 3
                req = r.get(b_url, verify=False)
                actual_url = req.url
                status_code = req.status_code
                if actual_url == exp_url:
                    info = {
                        'matching': True,
                        'expected_url': exp_url,

                        'actual_url': actual_url,
                        'base_url': b_url,
                        'status_code': status_code
                    }
                    result.append(info)
                    output_true = [{
                        'matching': True,
                        'expected_url': exp_url,
                        'actual_url': actual_url,
                        'status_code': status_code
                    }
                    ]
                    print(Fore.GREEN + str(count) + ' ' + str(output_true))
                    correct_links += 1
                elif actual_url == b_url:
                    info = {
                        'matching': "THE SAME PAGE",
                        'expected_url': exp_url,
                        'actual_url': actual_url,
                        'base_url': b_url,
                        'status_code': status_code
                    }
                    result.append(info)
                    output_same = [{
                        'matching': "THE SAME PAGE",
                        'expected_url': exp_url,
                        'actual_url': actual_url,
                        'base_url': b_url,
                        'status_code': status_code
                    }]
                    print(Fore.CYAN + str(count) + ' ' + str(output_same))
                    same_page += 1
                else:
                    info = {
                        'matching': False,
                        'expected_url': exp_url,
                        'actual_url': actual_url,
                        'base_url': b_url,
                        'status_code': status_code
                    }
                    result.append(info)
                    output_false = [{
                        'matching': "False",
                        'expected_url': exp_url,
                        'actual_url': actual_url,
                        'base_url': b_url,
                        'status_code': status_code
                    }]
                    print(Fore.RED + str(count) + ' ' + str(output_false))
                    incorrect_links += 1
                count += 1

        except TooManyRedirects:
            print(Fore.RED + "TOO MANY REDIRECTS FOR --> " + b_url)
            info = {
                'matching': "TOO MANY REDIRECTS",
                'expected_url': exp_url,

                'actual_url': b_url,
                'base_url': b_url,
                'status_code': None
            }
            result.append(info)

    print(Style.RESET_ALL)
    print("Checking is finished ...")
    statistics = [{
        'Quantity of Test URLs': len(base_url),
        'Correct redirects': correct_links,
        'Incorrect redirects': incorrect_links,
        'Redirect to the same page': same_page
    }]
    print("Statistics: " + str(statistics) + '\n')

    return result, statistics


# function for get data from config file
def read_config():
    params = []
    f = open('config.txt', 'r')
    data = f.readlines()
    info = [line.rstrip() for line in data]
    for row in info:
        params.append(row)
    print(params)
    return params


# Function for write result
# Function takes 2 arguments: 1) result list; 2) Name of result file
def file_write(result, statistics, file_name):
    try:
        dir_name = 'reports'
        os.makedirs(dir_name)
        print("Directory ", dir_name, " is Created ")
    except FileExistsError:
        pass
    with open(f'reports/{file_name}', 'w', encoding='utf-8', newline='') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(
            ('Quantity of Test URLs', 'Correct redirects', 'Incorrect redirects', 'Redirect to the same page'))
        for value in statistics:
            a_pen.writerow((value['Quantity of Test URLs'], value['Correct redirects'], value['Incorrect redirects'],
                            value['Redirect to the same page']))
        a_pen.writerow(('Base URl', 'Expected URL', 'Actual URL', 'Assertation', 'Status Code'))
        for row in result:
            a_pen.writerow(
                (row['base_url'], row['expected_url'], row['actual_url'], row['matching'], row['status_code']))
    print(f"Writing is finished!!")
    absolute_file_path = os.path.abspath(os.path.join(dir_name)) + '\\' + file_name
    print(f"Location: {absolute_file_path}")


try:
    init()
    print("--- Script is running!!! ---")
    parameter = read_config()
    file = parameter[0]
    save_name = parameter[1]
    domain = parameter[2]
    info = read_csv(file, domain)
    base_url_list = info[0].get('base_urls')
    print('Quantity of Test URLs: ' + str(len(base_url_list)))
    expected_url_list = info[-1].get('expected_urls')
    result, statistic = check_redirects(base_url=base_url_list, expected_url=expected_url_list)
    file_write(result=result, statistics=statistic, file_name=save_name)
    input('Press ENTER to exit')
except Exception as e:
    file_write(result=result, file_name=save_name)
    print('Error:\n', traceback.format_exc())
    input('Press ENTER to exit')
