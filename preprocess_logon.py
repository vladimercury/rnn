import yaml
import csv


def load_files_info():
    with open("files.yaml", "r") as file:
        return yaml.load(file)


def load_logon_info(logon_file_name):
    print("Loading logon from %s..." % logon_file_name, end="")
    logon_dict = dict()
    with open(logon_file_name, "r") as file:
        csv_reader = csv.reader(file, delimiter=",", quotechar='"')
        for csv_row in csv_reader:
            if len(csv_row) >= 5:
                _, logon_date, logon_user, __, logon_state, *logon_extra = csv_row
                logon_user_id = logon_user.split("/")[-1]
                if logon_user_id not in logon_dict:
                    logon_dict[logon_user_id] = list()
                logon_dict[logon_user_id].append((logon_date, logon_state))
    print("OK")
    return logon_dict


def save_logon_info(logon_dir, logon_info):
    for user_id, records in logon_info.items():
        print("Saving logon to %s/%s.csv..." % (logon_dir, user_id), end="")
        with open("%s/%s.csv" % (logon_dir, user_id), "w") as file:
            csv_writer = csv.writer(file, delimiter=",", quotechar='"')
            for record in records:
                csv_writer.writerow(record)
        print("OK")


files = load_files_info()
http = load_logon_info(files["input"]["logon"])
save_logon_info(files["preproc"]["logon"], http)
