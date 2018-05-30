import matplotlib.pyplot as pt
import csv

# AAALSTM = "models/AAA0371/lstm-stat.csv"
# AAAGRU = "models/AAA0371/gru-stat.csv"
# AAARNN = "models/AAA0371/rnn-stat.csv"
# CGMLSTM = "models/CGM0994/lstm-stat.csv"
# CGMGRU = "models/CGM0994/gru-stat.csv"
# KEELSTM = "models/KEE0997/lstm-stat.csv"
#
# INPUT_FILES = [
#     ("AAA GRU", AAAGRU, "red"),
#     ("AAA LSTM", AAALSTM, "green"),
#     ("AAA RNN", AAARNN, "blue")
# ]

LSTM = "models/hour/AAA0371/lstm-stat-r2.csv"
LSTMRND = "models/hour/AAA0371-rnd/lstm-stat-r2.csv"

HOUR_GRU = "models/hour/AAA0371/gru-stat-r2.csv"

HOUR_RNN = "models/hour/AAA0371/rnn-stat-r2.csv"

WEEK_GRU = "models/weekday/AAA0371/gru-stat-r2.csv"

MINUTE_GRU = "models/minute/AAA0371/gru-stat-r2.csv"
MINUTE_RNN = "models/minute/AAA0371/rnn-stat-r2.csv"
MINUTE_LSTM = "models/minute/AAA0371/lstm-stat-r2.csv"

INPUT_FILES = [
    ("minute GRU r2", MINUTE_GRU, "black"),
    ("minute RNN r2", MINUTE_RNN, "red"),
    ("minute LSTM r2", MINUTE_LSTM, "blue")
]


for name, input_file, color in INPUT_FILES:
    pre_cycles = 0
    x_list = list()
    y_train = list()
    y_test = list()
    with open(input_file, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            date, cycles, train_score, test_score, measure, *extra = row
            pre_cycles += int(cycles)
            x_list.append(pre_cycles)
            y_train.append(float(train_score))
            y_test.append(float(test_score))
    pt.plot(x_list, y_train, label=name + " train", linestyle="dashed", color=color)
    pt.plot(x_list, y_test, label=name + " test", color=color)
pt.legend()
pt.show()
