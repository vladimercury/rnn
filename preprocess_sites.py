import yaml
import csv


def load_files_info():
    with open("files.yaml", "r") as file:
        return yaml.load(file)


def load_sites_info(http_file_name):
    print("Loading sites from %s..." % http_file_name, end="")
    sites_set = set()
    with open(http_file_name, "r") as file:
        csv_reader = csv.reader(file, delimiter=",", quotechar='"')
        for csv_row in csv_reader:
            if len(csv_row) >= 5:
                http_url = csv_row[4]
                sites_set.add(http_url)
    print("OK")
    return [(y,) for y in sorted(sites_set)]


def save_sites_info(sites_file, sites_info):
    print("Saving http to %s..." % sites_file, end="")
    with open(sites_file, "w") as file:
        csv_writer = csv.writer(file, delimiter=",", quotechar='"')
        for record in sites_info:
            csv_writer.writerow(record)
    print("OK")


files = load_files_info()
sites = load_sites_info(files["input"]["http"])
save_sites_info(files["other"]["sites"], sites)
