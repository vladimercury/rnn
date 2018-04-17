import csv
import re
from datetime import datetime


INPUT_FILE = "data/logon.csv"
OUTPUT_DIR = "parsed/"
USER_NAME = "AAA0371"

regex = re.compile("[^0-9]+")

with open(OUTPUT_DIR + USER_NAME + ".csv", "w") as output:
    csv_writer = csv.writer(output, delimiter=",", quotechar='"')
    csv_writer.writerow("day,mon,yr,hr,min,sec,pc,logon".split(","))
    with open(INPUT_FILE, "r") as file:
        csv_reader = csv.reader(file, delimiter=",", quotechar='"')
        for row in csv_reader:
            break
        for row in csv_reader:
            if len(row) >= 5:
                _, date_str, user, pc, state, *extra = row
                if user.endswith(USER_NAME):
                    date = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")
                    csv_writer.writerow((date.day, date.month, date.year, date.hour,
                                         date.minute, date.second, regex.sub("", pc), int(state == "Logon")))
