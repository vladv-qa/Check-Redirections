import requests
import csv
from colorama import init, Fore, Style
import traceback
import os


def read_csv(file_name, domain):
    print("Reading information from file ...")
    data_list = []
    base_urls = []
    expected_urls = []
    with open(f'{file_name}', 'r', encoding="utf8") as file:
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


def file_write(result, file_name):
    try:
        dir_name = 'reports'
        os.makedirs(dir_name)
        print("Directory ", dir_name, " is Created ")
    except FileExistsError:
        pass
    with open(f'reports/{file_name}', 'w', encoding='utf-8', newline='') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('Base URl', 'Expected URL', 'Actual URL', 'Assertation', 'Status Code'))
        for row in result:
            a_pen.writerow(
                (row['base_url'], row['expected_url'], row['actual_url'], row['matching'], row['status_code']))
    print(f"Writing is finished!!")
    absolute_file_path = os.path.abspath(os.path.join(dir_name)) + '\\' + file_name
    print(f"Location: {absolute_file_path}")


def check_redirects(base_url, expected_url):
    print("Start checking ...")
    correct_links = 0
    uncorrect_links = 0
    same_page = 0
    result = []
    count = 1
    for b_url, exp_url in zip(base_url, expected_url):

        try:
            if b_url == exp_url:
                pass
            else:
                req = requests.get(b_url)
                actual_url = req.url
                status_code = req.status_code
        except ConnectionError:
            print('Seems like dns lookup failed..')
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
            uncorrect_links += 1
        count += 1

    print(Style.RESET_ALL)
    print("Checking is finished ...")
    statistics = [{
        'Quantity of Test URLs': len(base_url),
        'Correct redirects': correct_links,
        'Incorrect redirects': uncorrect_links,
        'Redirect to the same page': same_page
    }]
    print("Statistics: " + str(statistics) + '\n')
    return result


def read_config():
    params = []
    f = open('config.txt', 'r')
    data = f.readlines()
    info = [line.rstrip() for line in data]
    for row in info:
        params.append(row)
    print(params)
    return params


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
    result = check_redirects(base_url=base_url_list, expected_url=expected_url_list)
    file_write(result=result, file_name=save_name)
    input('Press ENTER to exit')
except Exception as e:
    file_write(result=result, file_name=save_name)
    print('Error:\n', traceback.format_exc())
    input('Press ENTER to exit')
