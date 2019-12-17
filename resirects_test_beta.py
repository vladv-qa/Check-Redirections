import csv
from colorama import init, Fore, Style
import traceback
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import time
from requests.exceptions import TooManyRedirects
import matplotlib.pyplot as plt


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


# make GET request and return redirected URL from response
def get_url(url):
    try:
        r = requests.Session()
        r.max_redirects = 3
        response = r.get(url, verify=False)
        red_url = response.url
        return red_url
    except TooManyRedirects:
        print("TOO MANY REDIRECTS FOR --> " + str(url))
        return 'Exception: Too many redirects'


# this function takes base urls list, call get_url() function and after that creating list of redirected URLs
def get_redirected_urls(base_url):
    print("Making redirects ...")
    with ThreadPoolExecutor(max_workers=50) as pool:
        redirected_urls = (list(pool.map(get_url, base_url)))
        return redirected_urls


# function takes 3 parameters: 1) tested URLs list 2) redirected URLs list 3)expected URLs list
# after that URLs comparing and adding to result list
# function return RESULT list
def check_redirects(base_url, actual_urls, expected_urls):
    print("Start checking ...")
    correct_links = 0
    incorrect_links = 0
    same_page = 0
    result = []
    count = 1

    for ac_url, exp_url, b_url in zip(actual_urls, expected_urls, base_url):
        if ac_url == 'Exception: Too many redirects':
            info = {
                'matching': "TOO MANY REDIRECTS",
                'expected_url': exp_url,
                'actual_url': b_url,
                'base_url': b_url,
                'status_code': None
            }
            result.append(info)
        elif ac_url == exp_url:
            info = {
                'matching': True,
                'expected_url': exp_url,
                'actual_url': ac_url,
                'base_url': b_url,
            }
            result.append(info)
            output_true = [{
                'matching': True,
                'expected_url': exp_url,
                'actual_url': ac_url
            }
            ]
            # print(Fore.GREEN + str(count) + ' ' + str(output_true))
            correct_links += 1
        elif ac_url == b_url:
            info = {
                'matching': "THE SAME PAGE",
                'expected_url': exp_url,
                'actual_url': ac_url,
                'base_url': b_url
            }
            result.append(info)
            output_same = [{
                'matching': "THE SAME PAGE",
                'expected_url': exp_url,
                'actual_url': ac_url,
                'base_url': b_url
            }]
            # print(Fore.CYAN + str(count) + ' ' + str(output_same))
            same_page += 1
        else:
            info = {
                'matching': False,
                'expected_url': exp_url,
                'actual_url': ac_url,
                'base_url': b_url
            }
            result.append(info)
            output_false = [{
                'matching': "False",
                'expected_url': exp_url,
                'actual_url': ac_url,
                'base_url': b_url
            }]
            # print(Fore.RED + str(count) + ' ' + str(output_false))
            incorrect_links += 1
        count += 1
    print(Style.RESET_ALL)
    print("Checking is finished ...")
    statistics = [{
        'Quantity of Test URLs': len(base_url),
        'Correct redirects': correct_links,
        'Incorrect redirects': incorrect_links,
        'Redirect to the same page': same_page,
        'Duration': None
    }]
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
            ('Quantity of Test URLs', 'Correct redirects', 'Incorrect redirects', 'Redirect to the same page', 'Duration'))
        for value in statistics:
            a_pen.writerow((value['Quantity of Test URLs'], value['Correct redirects'], value['Incorrect redirects'],
                            value['Redirect to the same page'], value['Duration']))
        a_pen.writerow(('Base URl', 'Expected URL', 'Actual URL', 'Assertation'))
        for row in result:
            a_pen.writerow(
                (row['base_url'], row['expected_url'], row['actual_url'], row['matching']))
    print(f"Writing is finished!!")
    absolute_file_path = os.path.abspath(os.path.join(dir_name)) + '\\' + file_name
    print(f"Location: {absolute_file_path}")

def pie_chart(statistic):
    labels = 'Correct', 'The same page', 'Incorrect'
    sizes = [statistic[0]['Correct redirects'], statistic[0]['Redirect to the same page'],
             statistic[0]['Incorrect redirects']]
    colors = ['green', 'blue', 'red']
    patches, texts = plt.pie(sizes, colors=colors, shadow=True, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
    ...

try:
    init()
    start = time.time()
    print("--- Script is running!!! ---")
    parameter = read_config()
    file = parameter[0]
    save_name = parameter[1]
    domain = parameter[2]
    info = read_csv(file, domain)
    base_url_list = info[0].get('base_urls')
    print('Quantity of Test URLs: ' + str(len(base_url_list)))
    expected_url_list = info[-1].get('expected_urls')
    actual_urls_list = get_redirected_urls(base_url=base_url_list)
    final_result, statistic = check_redirects(base_url=base_url_list, actual_urls=actual_urls_list,
                                              expected_urls=expected_url_list)
    work_time = str(f'{time.time() - start : .2f} seconds')
    statistic[0]['Duration'] = work_time
    pie_chart(statistic)
    file_write(result=final_result, statistics=statistic, file_name=save_name)
    input('Press ENTER to exit')

except Exception as e:
    print('Error:\n', traceback.format_exc())
    input('Press ENTER to exit')
