from datetime import datetime


class CSVRowParser:
    def __init__(self, config: list):
        self.__pc_dict = dict()
        self.__pc_counter = 1

        self.__weekday = "weekday" in config
        self.__hour = "hour" in config
        self.__pc = "pc" in config
        self.__logon = "logon" in config

    def parse(self, row):
        date_str, pc_number, logon_state, *extra = row
        date = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")

        output = list()
        if self.__weekday:
            output.append(date.weekday())
        if self.__hour:
            output.append(date.hour)
        if self.__pc:
            if pc_number not in self.__pc_dict:
                self.__pc_dict[pc_number] = self.__pc_counter
                self.__pc_counter += 1
            output.append(self.__pc_dict[pc_number])
        if self.__logon:
            output.append(int(logon_state))

        return tuple(output)

    def batch_parse(self, rows):
        return [self.parse(row) for row in rows]
