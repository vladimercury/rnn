from rnn import Config, CSVRowParser, DistributedReader, DistributedTrainer, Estimator
import time
from numpy import around


def max_index(lst):
    mx, mxi = lst[0], 0
    for i in range(len(lst)):
        if lst[i] > mx:
            mx, mxi = lst[i], i
    return mxi


def index_chart(lst, terminate):
    tfd = [(i, lst[i]) for i in range(len(lst))]
    std = sorted(tfd, key=lambda x: -x[1])
    ctd = [x[0] for x in std]
    allowed = min(int(max(1, len(std) * terminate)), len(ctd) - 1)
    return ctd[:allowed]


config = Config("config-pc-check.yaml")

train_lines_no = (config.input_file_lines_no * config.train_set_percentage) // 100
reader = DistributedReader(input_file_name=config.input_file_name, lines_number=train_lines_no,
                           max_chunk_size=config.max_chunk_size)
parser = CSVRowParser(config=config.input_vector)

chunk = reader.next_chunk()

# PC
pc_data = parser.batch_parse_pc_spec(chunk)
all_anom = parser.batch_parse_anomaly(chunk)[config.look_back_shift:]
pc_anom = [1 if x == 1 or x == 3 else 0 for x in all_anom]
hr_anom = [1 if x == 2 or x == 3 else 0 for x in all_anom]
merge_anom = [1 if x == 3 else 0 for x in all_anom]

pc_trainer = DistributedTrainer(model_class=config.model_type, row_shape=len(pc_data[0]),
                                model_file_path=config.model_file_name, look_back_shift=config.look_back_shift,
                                epoch_number=config.iterations, verbose_level=3)

pc_test_x, pc_test_y = pc_trainer.prepare_x_y(pc_data)
pc_test_pred = pc_trainer.predict(pc_test_x)
pc_anom_predict = [0] * len(pc_anom)


for i in range(len(pc_test_y)):
    exp = pc_test_y[i]
    pred = pc_test_pred[i]
    mi = max_index(exp)
    if exp[mi] == 0:
        pc_anom_predict[i] = 1
    else:
        alw = index_chart(pred, 0)
        if mi not in alw:
            pc_anom_predict[i] = 1

found = 0
false = 0
miss = 0
pc_res = list(map(int, [pc_anom[i] == pc_anom_predict[i] for i in range(len(pc_anom))]))
for i in range(len(pc_anom)):
    if pc_anom_predict[i]:
        if pc_res[i]:
            #print("[\033[0;32mFOUND\033[0m]", i)
            found += 1
        else:
            #print("[\033[0;31mFALSE\033[0m]", i)
            false += 1
    elif not pc_res[i]:
        #print("[\033[0;33mMISS\033[0m] ", i)
        miss += 1


print("By PC")
print("Found %d anomalies (%.2f%% of all anomalies)" % (found, found / (found + miss) * 100))
print("Missed %d anomalies (%.2f%% of all anomalies)" % (miss, miss / (found + miss) * 100))
print("False %d anomalies (%.2f%% of all records)" % (false, false / len(pc_anom) * 100))

print(sum(pc_res) / len(pc_anom))


# PC
hr_data = parser.batch_parse(chunk)

hr_trainer = DistributedTrainer(model_class=config.model_type, row_shape=1,
                                model_file_path=config.model_file_name_h, look_back_shift=config.look_back_shift,
                                epoch_number=config.iterations, verbose_level=3)

hr_test_x, hr_test_y = hr_trainer.prepare_x_y(hr_data)
hr_test_pred = hr_trainer.predict(hr_test_x)

hr_test_pred = around(hr_trainer.inverse_transform(hr_test_pred)) * (hr_test_y[0] / hr_test_pred[0])
hr_test_y = around(hr_trainer.inverse_transform(hr_test_y))

for DIFF in (210,):
    hr_anom_predict = [0] * len(hr_anom)

    for i in range(len(hr_test_y)):
        diff = abs(hr_test_y[i] - hr_test_pred[i])
        if diff > 12 * 60:
            diff = 24 * 60 - diff
        if diff > DIFF:
            hr_anom_predict[i] = 1

    found = 0
    false = 0
    miss = 0
    hr_res = list(map(int, [hr_anom[i] == hr_anom_predict[i] for i in range(len(hr_anom))]))
    for i in range(len(hr_anom)):
        if hr_anom_predict[i]:
            if hr_res[i]:
                #print("[\033[0;32mFOUND\033[0m]", i)
                found += 1
            else:
                #print("[\033[0;31mFALSE\033[0m]", i)
                false += 1
        elif not hr_res[i]:
            #print("[\033[0;33mMISS\033[0m] ", i)
            miss += 1

    print("By time, sensitivity %d minutes" % DIFF)
    print("Found %d anomalies (%.2f%% of all anomalies)" % (found, found / (found + miss) * 100))
    print("Missed %d anomalies (%.2f%% of all anomalies)" % (miss, miss / (found + miss) * 100))
    print("False %d anomalies (%.2f%% of all records)" % (false, false / len(pc_anom) * 100))

    print(sum(hr_res) / len(hr_anom))


counter = 0
right = 0
almost = 0
false = 0
for i in range(len(merge_anom)):
    if hr_anom_predict[i] and pc_anom_predict[i]:
        if merge_anom[i]:
            right += 1
        elif hr_anom[i] or pc_anom[i]:
            almost += 1
        else:
            false += 1
        counter += 1

print(counter, right, almost, false)