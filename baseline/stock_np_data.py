import numpy as np
import matplotlib.pyplot as plt
import csv

def get_stock_data_by_ticker(ticker):
    filename = "/root/data/historical/" + ticker + ".csv"
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        stock_data = [(day, float(info['Close'])) for day, info in enumerate(reader)]
    return np.array(stock_data)

if __name__ == "__main__":
    stock_np_arr = get_stock_data_by_ticker("GOOG")
    print stock_np_arr
