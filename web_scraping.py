from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--dns-prefetch-disable")


def addZero(num):
    if num < 10:
        num = '0' + str(num)
    return str(num)


def date_converter(y, m, d):
    converted_date = str(y) + "-" + addZero(m) + "-" + addZero(d)
    return converted_date


chromedriver_path = "chromedriver"
driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)

cities = [['izmir', "311046", "5417"], ['istanbul', "745044", "5328"], ['antalya', "323777", "5459"],
          ['zonguldak', "737022", "5306"], ['erzurum', "315368", "5356"], ['konya', "306571", "5432"]]
city = cities[1]
gid = '?gid=' + city[1]
station = '&station=' + city[2] + "&date="

month = 13
data = pd.DataFrame(
    {'Date': [], 'City': [], 'Enlem': [], 'Boylam': [], 'Yükseklik': [], 'Sıcaklık': [], 'Hissedilir Sıcaklık': [],
     'Bağıl Nem': [], 'Çiğ oluşma derecesi': [], 'Basınç': [], 'Durum': []})

for i in range(2019, 2022):
    if i == 2021:
        month = 6
    for j in range(1, month):
        for k in range(1, 32):
            date = date_converter(i, j, k)
            print(date)
            url = "https://tr.freemeteo.com/havadurumu/" + city[0] + "/history/daily-history/" + gid + station + date + "&language=turkish&country=turkey"
            try:
                driver.get(url)
            except TimeoutException as ex:
                print(ex.Message)
                driver.navigate().refresh()
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete')

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            if not any(soup):
                driver.navigate().refresh()

            date_data = soup.find('span', class_="station").find('a', class_='show-station-map')
            rows = soup.find('table', class_="daily-history").find_all('tr')

            for m in range(1, len(rows)):
                cols = rows[m].find_all('td')
                weather = cols[9].contents[1]
                cols = [elm.text.strip() for elm in cols]
                cols.pop(3), cols.pop(3), cols.pop(6)
                data.loc[len(data)] = [date + " " + cols[0] + ":00", city[0], date_data['data-lat'],
                                       date_data['data-lon'],
                                       date_data['data-elevation']] + cols[1:6] + [weather]


data['Basınç'] = data['Basınç'].replace({"mb": "", ",": "."}, regex=True)
data['Yükseklik'] = data['Yükseklik'].replace({"m": ""}, regex=True)
data['Bağıl Nem'] = data['Bağıl Nem'].replace({"%": ""}, regex=True)
cols_to_check = ['Sıcaklık', 'Hissedilir Sıcaklık', 'Çiğ oluşma derecesi']
data[cols_to_check] = data[cols_to_check].replace({'°C': ''}, regex=True)

data.to_csv(r'istanbul.csv', index=False)
