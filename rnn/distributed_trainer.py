from keras.layers import RNN, Dense
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler
import numpy


class DistributedTrainer:
    """
    Distributed RNN Trainer

    # Arguments
        model: keras.layers.RNN
            The model to train
        row_parser: function
            Function that parses csv row from input file and returns tuple of numbers with length = row_shape
        row_shape: int
            Number of items in tuple that represents parsed row
        look_back_shift: int
            Shift between X and Y
        epoch_number: int
            Number of iteration for each train
        verbose_level: int
            Model logging level
    """

    def __init__(self, model_class: RNN, row_shape: int, model_file_path: str,
                 look_back_shift: int = 1, epoch_number: int = 100, verbose_level: int = 2):
        self.__row_shape = row_shape

        self.__look_back_shift = look_back_shift
        self.__epoch_no = epoch_number

        self.__model = None
        self.__model_class = model_class

        self.__model_file_path = model_file_path

        self.__scaler = MinMaxScaler(feature_range=(0, 1))
        self.__verbose = verbose_level

        self._load_or_create()

    def _create_model(self):
        self.__model = Sequential()
        self.__model.add(self.__model_class(self.__row_shape, input_shape=(1, self.__row_shape)))
        self.__model.add(Dense(self.__row_shape))
        self.__model.compile(loss='mean_squared_error', optimizer='adam')

    def _load_or_create(self):
        try:
            self.__model = load_model(self.__model_file_path)
        except OSError:
            print("Loading model failed. Creating new one")
            self._create_model()

    def train(self, train_data):
        train_x, train_y = self.prepare_x_y(train_data)
        self.__model.fit(train_x, train_y, epochs=self.__epoch_no, batch_size=1, verbose=self.__verbose)
        return train_x, train_y

    def predict(self, x_data):
        return self.__model.predict(x_data)

    def inverse_transform(self, data):
        return self.__scaler.inverse_transform(data)

    def prepare_x_y(self, data):
        prepared = numpy.array(data)
        prepared = prepared.astype('float32')
        if len(prepared.shape) == 1:
            prepared = prepared.reshape(-1, 1)
        prepared = self.__scaler.fit_transform(prepared)

        data_x, data_y = prepared[:-self.__look_back_shift], prepared[self.__look_back_shift:]
        data_x = numpy.reshape(data_x, (data_x.shape[0], 1, data_x.shape[1]))

        return data_x, data_y

    def save(self):
        self.__model.save(self.__model_file_path)
