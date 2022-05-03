import json
import requests
import time
from datetime import datetime
from db_connection import db_connection
import concurrent.futures
from urllib.parse import urlparse

connection = db_connection()
cursor = connection.cursor()

cpcurr_code = {'BTC': 189, 'BCH': 215, 'ETH': 195, 'DASH': 199, 'LTC': 191, 'XRP': 197}
curr_code = {'UAH': 85, 'USD': 12, 'EUR': 17, 'GBP': 3}

def take_urls():
    urls = []

    # SQL-запрос для создания новой таблицы:
    create_table_query = '''CREATE TABLE IF NOT EXISTS bitcoin
                          (ID SERIAl NOT NULL PRIMARY KEY,
                          DATE_TIME     TIMESTAMP NOT NULL,
                          CP_CURR       VARCHAR NOT NULL,
                          CURR          VARCHAR NOT NULL,
                          PRICE         FLOAT); '''

    cursor.execute(create_table_query)
    connection.commit()

    for key in cpcurr_code.items():
        for elem in curr_code.items():
            URL = f'https://ru.investing.com/currencyconverter/service/RunConvert?fromCurrency={key[1]}&toCurrency={elem[1]}&fromAmount=1&toAmount=39170&currencyType=1'
            urls.append(URL)

    return(urls)

def db_filling():
    while True:
        urls = take_urls()

        def get_wiki_page_existence(wiki_page_url):
            response = requests.get(url=wiki_page_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0', 'X-Requested-With': 'XMLHttpRequest'})

            page_status = "unknown"
            if response.status_code == 200:
                page_status = "exists"
            elif response.status_code == 404:
                page_status = "does not exist"

            parsedurl = urlparse(wiki_page_url)
            res_list = parsedurl.query.split('&')

            for i in range(3):
                del res_list[2]

            return response.text + "   -   " + str(res_list)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            futures = []
            res = []
            for url in urls:
                futures.append(executor.submit(get_wiki_page_existence, wiki_page_url=url))
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                result_list = result.split("   -   ")
                resulttemp = json.loads(result_list[0]).get('calculatedAmount')
                resulttmp = float(resulttemp.replace(',', '.'))
                res.append(resulttmp)
                currencies1 = (result_list[1]).split('.')
                currencies2 = currencies1[0].split('=')
                cryptcurr = currencies2[1].split("'")[0]
                curr = currencies2[2].split("'")[0]

                final_crypt = None
                for key in cpcurr_code:
                    if cpcurr_code[key] == int(cryptcurr):
                        final_crypt = key

                final_curr = None
                for key in curr_code:
                    if curr_code[key] == int(curr):
                        final_curr = key

                now = datetime.now().isoformat(' ', 'minutes')
                dat = datetime.strptime(now, "%Y-%m-%d %H:%M")

                values = ({'cur_time': dat, 'cp_curr':final_crypt, 'curr':final_curr ,'res': resulttmp})
                insert_table_query = '''INSERT INTO bitcoin(date_time, cp_curr, curr, price) VALUES(%(cur_time)s,%(cp_curr)s,%(curr)s ,%(res)s)'''
                cursor.execute(insert_table_query, values)
                connection.commit()
            time.sleep(60)








