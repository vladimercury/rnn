from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, GRU, SimpleRNN
from datetime import datetime
import matplotlib.pyplot as plt
import time
import math
import csv
import numpy

# ИСПОЛЬЗУЕМАЯ МОДЕЛЬ
MODEL = LSTM
#MODEL = GRU
#MODEL = SimpleRNN

# Экономим оперативу, обучаем частями. Важно знать число непустых строк во входном файле

MODEL_FILE_NAME = 'models/model.h5'
STAT_FILE_NAME = 'models/model-stat.csv'
if MODEL is LSTM:
    MODEL_FILE_NAME = 'models/lstm.h5'
    STAT_FILE_NAME = 'models/lstm-stat.csv'
elif MODEL is GRU:
    MODEL_FILE_NAME = 'models/gru.h5'
    STAT_FILE_NAME = 'models/gru-stat.csv'
elif MODEL is SimpleRNN:
    MODEL_FILE_NAME = 'models/rnn.h5'
    STAT_FILE_NAME = 'models/rnn-stat.csv'

INPUT_FILE_NAME = "parsed/users/AAA0371.csv"  # Входной файл
INPUT_FILE_LEN = 844  # Число непустых строк в файле

CHUNK_SIZE = 800  # Размер куска для обучения
CHUNKS_NUM = 800 // CHUNK_SIZE  # Число кусков в обучающем множестве
MAX_TEST_SIZE = 100  # Максимальный размер тестового множества
LOOK_BACK = 1  # Величина сдвига
ITERATIONS = 100  # Число итераций обучения
SAVE_TO_FILE = True  # Сохранять ли графики в файл

SHAPE = 4  # Размер подаваемых на вход векторов
LABELS = ['weekday', 'hours', 'pc', 'state']

# SHAPE = 3
# LABELS = ['hours', 'pc', 'state']


pc_counter = 1
pc_dict = dict()
data_scaler = MinMaxScaler(feature_range=(0, 1))


def remaining(seconds):
    temp_val = seconds
    temp_res = list()
    for div, label in ((3600, "h"), (60, "m"), (1, "s")):
        if temp_val > div:
            temp_res.append("%d %s" % (temp_val // div, label))
            temp_val %= div
    return ' '.join(temp_res)


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
    if len(raw_row) >= 3:
        date_str, pc, logon, *extra = raw_row
        if pc not in pc_dict:
            pc_dict[pc] = pc_counter
            pc_counter += 1
        date = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")
        return date.weekday(), date.hour, pc_dict[pc], int(logon)
        #return  date.hour, pc_dict[pc], int(logon)
    return None


try:
    model = load_model(MODEL_FILE_NAME)
    with open(STAT_FILE_NAME, "a") as stat_file:
        pass
except (OSError, FileNotFoundError):
    with open(STAT_FILE_NAME, "w") as stat_file:
        print("iter,train_score,test_score", file=stat_file)
    model = Sequential()
    model.add(MODEL(4, input_shape=(1, SHAPE)))
    model.add(Dense(SHAPE))
    model.compile(loss='mean_squared_error', optimizer='adam')


with open(INPUT_FILE_NAME) as file:
    csv_reader = csv.reader(file)
    for csv_row in csv_reader:
        break # Avoid first line

    train_x, train_y = numpy.zeros(0), numpy.zeros(0)
    chunk_diff = 0
    for chunk_id in range(CHUNKS_NUM):
        print("\nChunk %d / %d Training..." % (chunk_id + 1, CHUNKS_NUM))
        temp_time = time.time()
        if chunk_id:
            print("Remaining ~%s" % remaining((chunk_diff / chunk_id) * (CHUNKS_NUM - chunk_id)))
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
        model.fit(train_x, train_y, epochs=ITERATIONS, batch_size=1, verbose=2)
        chunk_diff += time.time() - temp_time

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

model.save(MODEL_FILE_NAME)

train_predict = model.predict(train_x)
test_predict = model.predict(test_x)

train_predict = data_scaler.inverse_transform(train_predict)
train_y = data_scaler.inverse_transform(train_y)
test_predict = data_scaler.inverse_transform(test_predict)
test_y = data_scaler.inverse_transform(test_y)

# calculate root mean squared error
train_score = r2_score(train_y, train_predict)
print('Train Score: %.2f' % train_score)
test_score = r2_score(test_y, test_predict)
print('Test Score: %.2f' % test_score)

with open(STAT_FILE_NAME, "a") as stat_file:
    print("%d,%f,%f" % (ITERATIONS, train_score, test_score), file=stat_file)

for i in range(SHAPE):
    plt.plot(train_predict[:, i], label="Pred " + LABELS[i])
    plt.plot(train_y[:, i], label="Exp " + LABELS[i])
plt.legend()
if SAVE_TO_FILE:
    plt.savefig('1.png')
plt.figure()
for i in range(SHAPE):
    plt.plot(test_predict[:, i], label="Pred " + LABELS[i])
    plt.plot(test_y[:, i], label="Exp " + LABELS[i])
plt.legend()
if SAVE_TO_FILE:
    plt.savefig('2.png')
plt.show()
