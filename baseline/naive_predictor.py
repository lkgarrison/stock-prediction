# A naive baseline predictor for stock prices

import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.signal import argrelextrema
from dateutil import parser as dateparser

TRAINING_DATA_STOP_DATE = '2015-01-01'
TESTING_DATA_STOP_DATE = '2016-07-01'

# reads in csv csv file of stock data for given ticker
# returns an array of tuples in the form: (day number, closing price)
# the oldest day is marked as day 1
def get_stock_data_by_ticker(ticker, stop_date):
    filename = "../data/historical/" + ticker + ".csv"
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        csv_data = [row for row in reader]
        csv_data.reverse()
        stock_data = list()
        for day, info in enumerate(csv_data):
            if info['Date'] < stop_date:
                stock_data.append((day, float(info['Close'])))

    return np.array(stock_data)


# returns the number of local maxima + the number of local minimums
# in the array of stock data (tuples)
def get_number_of_extrema(stock_data):
    # stock_values contains only the stock price. it is just an array, not an array of tuples
    stock_values = np.array(map(lambda x: x[1], stock_data))

    return len(argrelextrema(stock_values, np.greater)[0]) + len(argrelextrema(stock_values, np.less)[0])


# returns a line of best fit for the last roughly 100 days of the training data
# this is used to predict the next day
def get_line_of_best_fit(training_data):
    most_recent_data = np.array(training_data[-125:])
    num_extrema = get_number_of_extrema(most_recent_data)

    x = most_recent_data[:,0]
    y = most_recent_data[:,1]

    # fit a polynomial w/ # degrees based on # min + max of data
    z = np.polyfit(x, y, num_extrema)
    f = np.poly1d(z)

    return f


# try to predict first day that isn't already known
def get_day_to_predict(training_data, num_days_forward=1):
    return get_last_known_day(training_data) + num_days_forward


# returns the last known day number for the given stock data
def get_last_known_day(data):
    return data[-1][0]


def calc_percent_error(correct_val, predicted_val):
    return abs(float(predicted_val - correct_val) / correct_val) * 100


if __name__ == "__main__":
    stock_data = get_stock_data_by_ticker('GOOG', TESTING_DATA_STOP_DATE)
    training_data = get_stock_data_by_ticker('GOOG', TRAINING_DATA_STOP_DATE)

    last_day_to_predict = get_last_known_day(stock_data)
    num_days_to_predict = len(stock_data) - len(training_data)

    # track stats to keep track of average percent error
    num_days_predicted = 0
    total_percent_error = 0
    num_days_forward = 5

    while num_days_to_predict >= num_days_forward:
        # get data for all days up to the day to predict
        training_data = stock_data[:-num_days_to_predict]

        f = get_line_of_best_fit(training_data)

        # predict next day, x days in advance
        day_to_predict = get_day_to_predict(training_data, num_days_forward)

        print f(day_to_predict), "vs", stock_data[int(day_to_predict)][1]
        total_percent_error += calc_percent_error(stock_data[int(day_to_predict)][1], f(day_to_predict))

        num_days_to_predict -= 1
        num_days_predicted += 1

    print "average percent error over", num_days_predicted, "predictions:", float(total_percent_error) / num_days_predicted
