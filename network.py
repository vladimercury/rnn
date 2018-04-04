from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import LSTM, Dense, GRU
import matplotlib.pyplot as plt
import math
import csv
import numpy

# DEFINES

# % of train data from all data
TRAIN_PERCENTAGE = 0.8

# look back for how many steps
LOOK_BACK = 1

# truncate dataset for faster computing
DATA_SET_SIZE = 50

# used model
MODEL = LSTM
# MODEL = GRU

# number of training iterations
ITERATIONS = 100

# saving graphs to file
SAVE_TO_FILE = False

# PROGRAM


def read_data():
    with open("preproc/logon/AAA0371.csv") as file:
        logon_data = list()
        csv_reader = csv.reader(file)
        for csv_row in csv_reader:
            if len(csv_row) >= 2:
                logon_date_str, logon_state_str, *extra = csv_row
                logon_date = datetime.strptime(logon_date_str, "%m/%d/%Y %H:%M:%S")
                logon_state = 1 if logon_state_str == "Logon" else 0
                logon_data.append((logon_date.day, logon_date.hour, logon_state))
        return logon_data


data = numpy.array(read_data()[:DATA_SET_SIZE])
data = data.astype('float32')
if len(data.shape) == 1:
    data = data.reshape(-1, 1)
scaler = MinMaxScaler(feature_range=(0, 1))
data = scaler.fit_transform(data)

train_size = int(len(data) * TRAIN_PERCENTAGE)
train_data, test_data = data[0:train_size], data[train_size:]

train_x, train_y = train_data[:-LOOK_BACK], train_data[LOOK_BACK:]
test_x, test_y = test_data[:-LOOK_BACK], test_data[LOOK_BACK:]

shape = train_x.shape[1]

train_x = numpy.reshape(train_x, (train_x.shape[0], 1, shape))
test_x = numpy.reshape(test_x, (test_x.shape[0], 1, shape))

model = Sequential()
model.add(MODEL(4, input_shape=(1, shape)))
model.add(Dense(shape))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(train_x, train_y, epochs=ITERATIONS, batch_size=1, verbose=3)

train_predict = model.predict(train_x)
test_predict = model.predict(test_x)

train_predict = scaler.inverse_transform(train_predict)
train_y = scaler.inverse_transform(train_y)
test_predict = scaler.inverse_transform(test_predict)
test_y = scaler.inverse_transform(test_y)

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
