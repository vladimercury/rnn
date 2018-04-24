import csv
import re
import yaml
import os

with open("parse.yaml", "r") as file:
    config = yaml.load(file)
    input_file_name = config["input_file_name"]
    output_dir = config["output_dir"]

regex = re.compile("[^0-9]+")
output = None
csv_writer = None

estimation = dict()

# estimate
with open(input_file_name, "r") as file:
    print("Estimating...")
    csv_reader = csv.reader(file, delimiter=",", quotechar='"')
    next(csv_reader)
    for row in csv_reader:
        if len(row) >= 5:
            _, date_str, user, pc, state, *extra = row
            current_user_name = user.split("/")[1]
            if current_user_name not in estimation:
                estimation[current_user_name] = 0
            estimation[current_user_name] += 1

user_name = max(estimation.items(), key=lambda x: x[1])[0]
print("User %s has the biggest number of lines" % user_name)

with open(input_file_name, "r") as file:
    lines_number = 0
    csv_reader = csv.reader(file, delimiter=",", quotechar='"')
    next(csv_reader)
    for row in csv_reader:
        if len(row) >= 5:
            _, date_str, user, pc, state, *extra = row
            if user_name is None:
                user_name = user.split("/")[1]
            if user.endswith(user_name):
                if output is None:
                    try:
                        os.makedirs(output_dir)
                    except FileExistsError:
                        pass
                    output_file_name = output_dir + "/" + user_name + ".csv"
                    output = open(output_file_name, "w")
                    csv_writer = csv.writer(output, delimiter=",", quotechar='"')
                    csv_writer.writerow("date,pc,logon".split(","))
                lines_number += 1
                csv_writer.writerow((date_str, regex.sub("", pc), int(state == "Logon")))

output.close()
print("Saved to %s" % output_file_name)
print("Lines: %d" % lines_number)
