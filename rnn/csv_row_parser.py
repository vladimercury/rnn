from datetime import datetime
from numpy import zeros


class CSVRowParser:
    def __init__(self, config: list):
        self.__pc_dict = dict()
        self.__pc_counter = 0

        self.__weekday = "weekday" in config
        self.__hour = "hour" in config
        self.__minute = "minute" in config
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
        if self.__minute:
            output.append(date.hour * 60 + date.minute)
        if self.__pc:
            if pc_number not in self.__pc_dict:
                self.__pc_dict[pc_number] = self.__pc_counter
                self.__pc_counter += 1
            num = self.__pc_dict[pc_number]
            self.__pc_counter = max(self.__pc_counter, num)
            output.append(pc_number)
        if self.__logon:
            output.append(int(logon_state))

        return output

    def batch_parse(self, rows):
        return [self.parse(row) for row in rows]

    def batch_parse_pc_spec(self, rows):
        parsed = [self.parse_pc(row) for row in rows]
        srt = sorted(self.__pc_dict.items(), key=lambda x: -x[1])
        shape = min(len(srt), 10)
        step = len(srt) // 10
        for i in range(shape):
            if i != shape - 1:
                part = srt[i*step:i*step + step]
            else:
                part = srt[i*step:]
            for key, value in part:
                self.__pc_dict[key] = i

        self.__pc_counter = shape
        for i in range(len(parsed)):
            num = parsed[i]
            parsed[i] = zeros(self.__pc_counter)
            parsed[i][self.__pc_dict[num]] = 1
        return parsed

    def batch_parse_fix(self, rows):
        parsed = [self.parse_pc_fix_dict(row) for row in rows]
        for i in range(len(parsed)):
            num = parsed[i]
            parsed[i] = zeros(self.__pc_counter)
            if num >= 0:
                parsed[i][num] = 1
        return parsed

    def parse_pc(self, row):
        date_str, pc_number, logon_state, *extra = row

        if pc_number not in self.__pc_dict:
            self.__pc_dict[pc_number] = 0
        self.__pc_dict[pc_number] += 1
        return pc_number

    def parse_pc_fix_dict(self, row):
        date_str, pc_number, logon_state, *extra = row

        if pc_number not in self.__pc_dict:
            return -1
        return self.__pc_dict[pc_number]

    def batch_parse_anomaly(self, rows):
        return [self.parse_anomaly(row) for row in rows]

    def parse_anomaly(self, row):
        date_str, pc_number, logon_state, *extra = row
        if len(extra):
            return int(extra[0])
        return 0

    @property
    def pc_dict(self):
        return self.__pc_dict
