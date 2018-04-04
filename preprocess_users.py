import yaml
import csv


def load_files_info():
    with open("files.yaml", "r") as file:
        return yaml.load(file)


def load_users(file_name):
    print("Loading users from %s..." % file_name, end="")
    users_dict = dict()
    with open(file_name, "r") as file:
        csv_reader = csv.reader(file, delimiter=",")
        next(csv_reader)  # skip first line
        for csv_row in csv_reader:
            if len(csv_row) >= 2:
                user_name, user_id, *user_extra = csv_row
                users_dict[user_id] = user_name
    print("OK")
    return users_dict


def extend_users(target, user_extension):
    for key, value in user_extension.items():
        if key in target:
            if value != target[key]:
                print("MERGE: Overriding key %s" % key)
                target[key] = value
        else:
            target[key] = value
    return target


def save_users(target_file_name, save_data):
    print("Saving users to %s..." % target_file_name, end="")
    with open(target_file_name, "w") as file:
        csv_writer = csv.writer(file, delimiter=",", quotechar="\"")
        for key, value in sorted(save_data.items()):
            csv_writer.writerow((key, value))
    print("OK")


users = dict()
files = load_files_info()
for user_file_name in sorted(files["input"]["users"]):
    extension = load_users(user_file_name)
    extend_users(users, extension)
save_users(files["preproc"]["users"], users)
