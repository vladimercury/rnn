from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import LSTM, Dense, GRU, SimpleRNN
import matplotlib.pyplot as plt
import math
import csv
import numpy

# Экономим оперативу, обучаем частями. Важно знать число непустых строк во входном файле

INPUT_FILE_NAME = "parsed/users/AAA0371.csv"  # Входной файл
INPUT_FILE_LEN = 844  # Число непустых строк в файле

CHUNK_SIZE = 50  # Размер куска для обучения
CHUNKS_NUM = 800 // CHUNK_SIZE  # Число кусков в обучающем множестве
MAX_TEST_SIZE = 100  # Максимальный размер тестового множества
LOOK_BACK = 1  # Величина сдвига
ITERATIONS = 10  # Число итераций обучения
SAVE_TO_FILE = False  # Сохранять ли графики в файл

SHAPE = 3  # Размер подаваемых на вход векторов

# ИСПОЛЬЗУЕМАЯ МОДЕЛЬ
MODEL = LSTM
# MODEL = GRU
# MODEL = SimpleRNN

pc_counter = 1
pc_dict = dict()
data_scaler = MinMaxScaler(feature_range=(0, 1))


def get_x_y(initial_data):
    data = numpy.array(initial_data)
    data = data.astype('float32')
    if len(data.shape) == 1:
        data = data.reshape(-1, 1)
    data = data_scaler.fit_transform(data)

    data_x, data_y = data[:-LOOK_BACK], data[LOOK_BACK:]
    data_x = numpy.reshape(data_x, (data_x.shape[0], 1, data_x.shape[1]))

    return data_x, data_y


def get_row_data(raw_row):
    global pc_counter
    if len(raw_row) >= 8:
        day, mon, year, hrs, mins, sec, pc, logon, *extra = raw_row
        if pc not in pc_dict:
            pc_dict[pc] = pc_counter
            pc_counter += 1
        return int(hrs), pc_dict[pc], int(logon)
    return None


model = Sequential()
model.add(MODEL(4, input_shape=(1, SHAPE)))
model.add(Dense(SHAPE))
model.compile(loss='mean_squared_error', optimizer='adam')


with open(INPUT_FILE_NAME) as file:
    csv_reader = csv.reader(file)
    for csv_row in csv_reader:
        break # Avoid first line

    train_x, train_y = numpy.zeros(0), numpy.zeros(0)
    for chunk_id in range(CHUNKS_NUM):
        print("\nChunk %d / %d Training..." % (chunk_id, CHUNKS_NUM))
        logon_data = list()
        chunk_counter = 0
        for csv_row in csv_reader:
            chunk_counter += 1
            row_data = get_row_data(csv_row)
            if row_data:
                logon_data.append(row_data)
            if chunk_counter >= CHUNK_SIZE:
                break
        train_x, train_y = get_x_y(logon_data)
        model.fit(train_x, train_y, epochs=ITERATIONS, batch_size=1, verbose=3)

    print("\nTest...")
    logon_data = list()
    counter = 0
    for csv_row in csv_reader:
        row_data = get_row_data(csv_row)
        if row_data:
            logon_data.append(row_data)
            counter += 1
        if counter >= MAX_TEST_SIZE:
            break
    test_x, test_y = get_x_y(logon_data)

model.save()

train_predict = model.predict(train_x)
test_predict = model.predict(test_x)

train_predict = data_scaler.inverse_transform(train_predict)
train_y = data_scaler.inverse_transform(train_y)
test_predict = data_scaler.inverse_transform(test_predict)
test_y = data_scaler.inverse_transform(test_y)

# calculate root mean squared error
train_score = math.sqrt(mean_squared_error(train_y, train_predict))
print('Train Score: %.2f RMSE' % train_score)
test_score = math.sqrt(mean_squared_error(test_y, test_predict))
print('Test Score: %.2f RMSE' % test_score)

plt.plot(train_predict)
plt.plot(train_y)
if SAVE_TO_FILE:
    plt.savefig('1.png')
plt.figure()
plt.plot(test_predict)
plt.plot(test_y)
if SAVE_TO_FILE:
    plt.savefig('2.png')
plt.show()
