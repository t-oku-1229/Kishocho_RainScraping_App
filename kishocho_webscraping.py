from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import os
from bs4 import BeautifulSoup
import requests
import time
import calendar


class RainDataExtractor:


    def __init__(self, prec_no, block_no, start_year, end_year):
        self.prec_no = str(prec_no)
        self.block_no = str(block_no)
        self.start_year = int(start_year)
        self.end_year = int(end_year)
        self.date_arr = []
        self.hourly_rain = []


    def convertmonth(self, imonth):
        if imonth < 10:
            month = '0' + str(imonth)
        else:
            month = str(imonth)

        return month


    def createdf(self, header):
        data = {"date": self.date_arr, str(header): self.hourly_rain}
        return pd.DataFrame(data)


    def rainmultiyear(self):

        if 'datetime_container' not in st.session_state:
            st.session_state.datetime_container = st.empty()

        for year in range(self.start_year, self.end_year + 1):
            start_datetime = datetime(year, 1, 1, 1, 0)
            end_datetime = datetime(year, 12, 31, 23, 59)
            current_datetime = start_datetime
         
            for month in range(1,13):
                end_day = calendar.monthrange(year,month)[1] + 1
         
                for day in range(1,end_day):
                    url = 'https://www.data.jma.go.jp/obd/stats/etrn/view/hourly_a1.php?prec_no=' + str(self.prec_no) + '&block_no=' + str(self.block_no) + "&year=" + str(year) + '&month=' + str(month) + '&day=' + str(day) + '&view='

                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,"html.parser")
                    _rain = soup.find_all('tr', class_ = 'mtx', style = 'text-align:right;')

                    st.session_state.datetime_container.write(str(year) + '年' + str(month) + '月' + str(day) + '日 のデータを取得中')

                    for hour in range(0,24):
                        flag = False
                        hour_value = _rain[hour]
                        data = hour_value.find_all('td', class_ = 'data_0_0')
                        rain_html = str(data[0])
                        rain = rain_html.replace('<td class="data_0_0">','').replace('</td>','')
                        if rain == '--':
                            rain = 0.0
                        self.hourly_rain.append(rain)
                        self.date_arr.append(current_datetime.strftime('%Y-%m-%d %H:%M'))
                        current_datetime += timedelta(hours=1)

                    time.sleep(0.5)

        # データフレームの作成
        return self.createdf('rain').to_csv(index=False).encode('shift_jis')


def main():
    # タイトルと説明
    st.title('気象庁 雨量取得Webアプリ')
    st.text('気象庁の雨量取得を行うためのWebアプリケーションを作成してみました。\n雨量情報を取得する機会があればぜひお使いください。')

    st.markdown("""
    ### 本アプリについて
    気象庁の雨量値を時間単位で取得できるWebアプリです。

    ### 取得手順
    1. 取得したい観測所の都道府県番号（URLの"prec_no"）とブロック番号（URLの"block_no"）を調べます。[例）朝倉](https://www.data.jma.go.jp/obd/stats/etrn/index.php?prec_no=82&block_no=0788&year=&month=&day=&view=)
    2. 取得したい年数を入力します。予め取得できる年数を確認しておくことをお勧めします。
    3. 入力情報に基づいて雨量データをスクレイピングします。\n
    ※ 日数ごとに1秒間の停止時間を設けているため、取得に時間を要します。\n
    ※ **:red[20年など、期間が長いとTimeoutでプログラムが止まる可能性があります。その場合は取得期間を短くしてお試し下さい。]**
    """)

    prec_no = st.text_input('▼観測所の都道府県番号（prec_no）：例）82')
    block_no = st.text_input('▼観測所のブロック番号（block_no）：例）0788')

    start_year_multi = st.text_input('開始年')
    end_year_multi = st.text_input('終了年')
    submit_btn_multi = st.button('▼取得開始')

    if submit_btn_multi:
        extractor_multi = RainDataExtractor(prec_no, block_no, start_year_multi, end_year_multi)
        text_placeholder = st.text('csvデータを作成中です...')
        csvdata = extractor_multi.rainmultiyear()
        new_text = 'csvデータの作成が完了しました'
        text_placeholder.text(new_text)
        st.download_button(
           "CSVダウンロード",
           csvdata,
           "result.csv",
           "text/csv",
           key='download-csv'
        )


if __name__ == '__main__':
    main()
