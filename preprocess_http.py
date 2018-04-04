import yaml
import csv


def load_files_info():
    with open("files.yaml", "r") as file:
        return yaml.load(file)


def load_http_info(http_file_name):
    print("Loading http from %s..." % http_file_name, end="")
    http_dict = dict()
    with open(http_file_name, "r") as file:
        csv_reader = csv.reader(file, delimiter=",", quotechar='"')
        for csv_row in csv_reader:
            if len(csv_row) >= 5:
                _, http_date, http_user, __, http_url, *http_extra = csv_row
                http_user_id = http_user.split("/")[-1]
                if http_user_id not in http_dict:
                    http_dict[http_user_id] = list()
                http_dict[http_user_id].append((http_date, http_url))
    print("OK")
    return http_dict


def save_http_info(http_dir, http_info):
    for user_id, records in http_info.items():
        print("Saving http to %s/%s.csv..." % (http_dir, user_id), end="")
        with open("%s/%s.csv" % (http_dir, user_id), "w") as file:
            csv_writer = csv.writer(file, delimiter=",", quotechar='"')
            for record in records:
                csv_writer.writerow(record)
        print("OK")


files = load_files_info()
http = load_http_info(files["input"]["http"])
save_http_info(files["preproc"]["http"], http)
