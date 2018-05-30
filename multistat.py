import matplotlib.pyplot as pt
import csv

DATA = [
    ("rnn", "models/AAA0371/rnn-stat.csv", "red"),
    ("lstm", "models/AAA0371/lstm-stat.csv", "green"),
    ("gru", "models/AAA0371/gru-stat.csv", "blue")
]

for name, path, color in DATA:
    pre_cycles = 0
    x_list = list()
    y_train = list()
    y_test = list()

    with open(path, "r") as file:
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
