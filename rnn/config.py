from keras.layers import LSTM, GRU, SimpleRNN
from sklearn.metrics import r2_score, mean_squared_error
import yaml

model_types = {
    "lstm": LSTM,
    "gru": GRU,
    "rnn": SimpleRNN
}

metric_types = {
    "r2": r2_score,
    "mse": mean_squared_error
}


class Config:
    def __init__(self, config_file_name: str):
        with open(config_file_name, "r") as file:
            self.__data = yaml.load(file)
        self.__input = self.__data["input"]
        self.__input_vector = self.__data["input_vector"]
        self.__model = self.__data["model"]

        self.__model_type = None
        model_type_name = self.__model["type"].lower()
        if model_type_name in model_types:
            self.__model_type = model_types[model_type_name]
        self.__model_name = model_type_name

        self.__metric_type = None
        metric_type_name = self.__model["metric"].lower()
        if metric_type_name in metric_types:
            self.__metric_type = metric_types[metric_type_name]
        self.__metric_name = metric_type_name

    @staticmethod
    def _safe_get(container: dict, key: str, default_value):
        if key in container:
            return container[key]
        return default_value

    @property
    def input_file_name(self):
        return self.__input["file_name"]

    @property
    def input_file_lines_no(self):
        return self.__input["lines_in_file"]

    @property
    def max_chunk_size(self):
        return self._safe_get(self.__input, "max_chunk_size", 500)

    @property
    def train_set_percentage(self):
        return self._safe_get(self.__input, "train_set_percentage", 90)

    @property
    def input_vector(self):
        return self.__input_vector

    @property
    def input_vector_length(self):
        return len(self.__input_vector)

    @property
    def model_type(self):
        return self.__model_type

    @property
    def model_file_name(self):
        return self.__model["dir"] + self.__model_name + ".h5"

    @property
    def look_back_shift(self):
        return self._safe_get(self.__model, "look_back", 1)

    @property
    def iterations(self):
        return self.__model["iterations"]

    @property
    def metric_type(self):
        return self.__metric_type

    @property
    def metric_type_name(self):
        return self.__metric_name

    @property
    def stat_file_name(self):
        return self.__model["dir"] + self.__model_name + "-stat.csv"
