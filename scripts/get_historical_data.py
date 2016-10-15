import os, sys
import csv

s_and_p_tickers = set()
yahoo_url = "http://chart.finance.yahoo.com/table.csv?s=GOOG&a=7&b=19&c=2004&d=9&e=14&f=2016&g=d&ignore=.csv"
yahoo_begin = "http://chart.finance.yahoo.com/table.csv?s="
yahoo_end = "&a=7&b=19&c=2004&d=9&e=14&f=2016&g=d&ignore=.csv"

def populate_companies(filename):
    with open(filename, 'r') as csvfile:
        fieldnames = ['Symbol','Name','Sector']
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        first_line = True
        for row in reader:
            if first_line:
                first_line = False
                continue
            s_and_p_tickers.add(row['Symbol'])

def wget_stock_data():
    for ticker in s_and_p_tickers:
        wget_str = 'wget -O ' + ticker + ".csv " + yahoo_begin + ticker + yahoo_end # wget -O GOOG.csv http://yahoo...GOOG...
        os.system(wget_str)


if __name__ == "__main__":
    populate_companies("constituents.csv")
    print("Beginning to grab stock data...")
    wget_stock_data()
    print("Collected all data.")
	
