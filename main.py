import requests
import csv

from bs4 import BeautifulSoup
from datetime import datetime

requests.packages.urllib3.disable_warnings()


def get_data(url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                  'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                      'like Gecko) Chrome/99.0.4844.82 Safari/537.36'
    }
    cur_data = datetime.now().strftime('%d-%m-%Y')
    response = requests.get(url=url, headers=headers)

    with open(file='data/index.html', mode='w') as file:
        file.write(response.text)

    with open(file='data/index.html', mode='r') as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    table = soup.find('table', id='ro5xgenergy')

    data_th = table.find('thead').find_all('tr')[-1].find_all('th')

    table_headers = ['Area']
    for dth in data_th:
        dth = dth.text.strip()
        table_headers.append(dth)

    with open(file=f'data/data_{cur_data}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            table_headers
        )

    tbody_trs = table.find('tbody').find_all('tr')

    ids = []
    data = []
    for tr in tbody_trs:
        area = tr.find('th').text.strip()
        data_by_month = tr.find_all('td')

        data = [area]
        for dbm in data_by_month:
            if dbm.find('a'):
                area_data = dbm.find('a').get('href')
                id = area_data.split('/')[4].split('?')[0]
                ids.append(id)
            elif dbm.find('span'):
                area_data = dbm.find('span').text.strip()
            else:
                area_data = 'None'

            data.append(area_data)

        with open(file=f'data/data_{cur_data}.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                data
            )

    with open(file='data/ids.txt', mode='w') as file:
        for id in ids:
            file.write(f'{id}\n')

    return 'Work done!'


def download_xlsx(file_path='data/ids.txt'):
    with open(file=file_path, mode='r') as file:
        ids = [line.strip() for line in file.readlines()]

    for num, id in enumerate(ids):
        headers = {
            'Host': 'data.bls.gov',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 '
                          'Firefox/98.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                      '*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://data.bls.gov',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Connection': 'close'
        }

        data = f'request_action=get_data&reformat=true&from_results_page=true&years_option' \
               f'=specific_years&delimiter=comma&output_type=multi&periods_option=all_periods' \
               f'&output_view=data&output_format=excelTable&original_output_type=default' \
               f'&annualAveragesRequested=false&series_id={id}'

        response = requests.post('https://data.bls.gov/pdq/SurveyOutputServlet', headers=headers,
                                 data=data, verify=False)

        with open(file=f'xlsx/{id}.xlsx', mode='wb') as file:
            file.write(response.content)

        print(f'{num + 1}/{len(ids)}')


def main():
    get_data(
        url='https://www.bls.gov/regions/midwest/data/AverageEnergyPrices_SelectedAreas_Table.htm')
    # download_xlsx()


if __name__ == '__main__':
    main()
