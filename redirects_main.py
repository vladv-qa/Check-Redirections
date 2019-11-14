import requests
import csv
from colorama import init, Fore, Style

init()


def read_csv(file_name, domain):
    print("Reading information from file ...")
    data_list = []
    base_urls = []
    expected_urls = []
    with open(f'{file_name}', 'r', encoding='utf-8') as file:
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
    with open(f'reports/{file_name}', 'w', encoding='utf-8', newline='') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('Base URl', 'Expected URL', 'Actual URL', 'Assertation'))
        for row in result:
            a_pen.writerow((row['base_url'], row['expected_url'], row['current_url'], row['matching']))
    print(f"Writing is finished!!")
    print(f"Location: /reports/{file_name}")


def check_redirects(base_url, expected_url):
    print("Start checking ...")
    result = []
    count = 1
    for b_url, exp_url in zip(base_url, expected_url):
        req = requests.get(b_url)
        current_url = req.url
        if current_url == exp_url:
            info = {
                'matching': True,
                'expected_url': exp_url,
                'current_url': current_url,
                'base_url': b_url
            }
            result.append(info)
            output_true = [{
                'matching': True,
                'expected_url': exp_url,
                'current_url': current_url
            }
            ]
            print(Fore.GREEN + str(count) + ' ' + str(output_true))
        elif current_url == b_url:
            info = {
                'matching': "THE SAME PAGE",
                'expected_url': exp_url,
                'current_url': current_url,
                'base_url': b_url
            }
            result.append(info)
            output_same = [{
                'matching': "THE SAME PAGE",
                'expected_url': exp_url,
                'current_url': current_url,
                'base_url': b_url
            }]
            print(Fore.CYAN + str(count) + ' ' + str(output_same))
        else:
            info = {
                'matching': False,
                'expected_url': exp_url,
                'current_url': current_url,
                'base_url': b_url
            }
            result.append(info)
            output_false = [{
                'matching': "THE SAME PAGE",
                'expected_url': exp_url,
                'current_url': current_url,
                'base_url': b_url
            }]
            print(Fore.RED + str(count) + ' ' + str(output_false))
        count +=1
    print(Style.RESET_ALL)
    print("Checking finished ...")

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


print("--- Script is running!!! ---")

parameter = read_config()
file = parameter[0]
save_name = parameter[1]
domain = parameter[2]
info = read_csv(file, domain)
base_url_list = info[0].get('base_urls')
expected_url_list = info[-1].get('expected_urls')
result = check_redirects(base_url=base_url_list, expected_url=expected_url_list)
file_write(result=result, file_name=save_name)
