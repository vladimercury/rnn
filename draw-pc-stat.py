import matplotlib.pyplot as pt
import csv

colors = ["blue", "red", "black", "green", "orange"]

INPUT_FILE = "pc/AAA0371/gru-stat-r2.csv"
data = dict()
with open(INPUT_FILE, "r") as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        train_score, test_score, iterations, name, *extra = row
        if name not in data:
            data[name] = {"iter": 0, "x": list(), "y_train": list(), "y_test": list()}
        current = data[name]
        current["iter"] += int(iterations)
        current["x"].append(current["iter"])
        current["y_train"].append(float(train_score))
        current["y_test"].append(float(test_score))

n = 0
for key, value in data.items():
    clr = None
    if n < len(colors):
        clr = colors[n]
    n += 1
    pt.plot(value["x"], value["y_train"], label=key + " train", linestyle="dashed", color=clr)
    pt.plot(value["x"], value["y_test"], label=key + " test", color=clr)
pt.legend()
pt.show()
