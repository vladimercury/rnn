from rnn import Config, CSVRowParser, DistributedReader, DistributedTrainer, Estimator
import time


def max_index(lst):
    mx, mxi = lst[0], 0
    for i in range(len(lst)):
        if lst[i] > mx:
            mx = lst[i]
            mxi = i
    return mxi


def min_index(lst):
    mn, mni = lst[0], 0
    for i in range(len(lst)):
        if lst[i] < mn:
            mn, mni = lst[i], i
    return mni


def index_chart(lst, terminate):
    tfd = [(i, lst[i]) for i in range(len(lst))]
    std = sorted(tfd, key=lambda x: -x[1])
    ctd = [x[0] for x in std]
    allowed = min(int(max(1, len(std) * terminate)), len(ctd) - 1)
    return ctd[:allowed]


def estimate_strict(exp, pred):
    n_all, n_acc = len(exp), 0
    for i in range(len(exp)):
        if max_index(exp[i]) == max_index(pred[i]):
            n_acc += 1
    return n_acc / n_all


def estimate_lenient(exp, pred):
    n_all, n_acc = len(exp), 0
    for i in range(len(exp)):
        mi = max_index(exp[i])
        if mi != min_index(pred[i]):
            n_acc += 1
    return n_acc / n_all


def do_estimate(exp, pred, terminate=0.0):
    n_all, n_acc = len(exp), 0
    for i in range(len(exp)):
        mi = max_index(exp[i])
        ic = index_chart(pred[i], terminate)
        if mi in ic:
            n_acc += 1
    return n_acc / n_all


now = time.time()
config = Config("config-pc.yaml")

train_lines_no = (config.input_file_lines_no * config.train_set_percentage) // 100
reader = DistributedReader(input_file_name=config.input_file_name, lines_number=train_lines_no,
                           max_chunk_size=config.max_chunk_size)
parser = CSVRowParser(config=config.input_vector)
estimator = Estimator(metric=config.metric_type, metric_name=config.metric_type_name,
                      stat_file_name=config.stat_file_name, do_round=config.round, do_class=config.classification_score)

chunk = reader.next_chunk()
data = parser.batch_parse_pc_spec(chunk)

trainer = DistributedTrainer(model_class=config.model_type, row_shape=len(data[0]),
                             model_file_path=config.model_file_name, look_back_shift=config.look_back_shift,
                             epoch_number=config.iterations, verbose_level=3)

train_x, train_y = trainer.train(data)
trainer.save()

parsed_test = parser.batch_parse_fix(reader.extra_data())
test_x, test_y = trainer.prepare_x_y(parsed_test)
train_predict = trainer.predict(train_x)
test_predict = trainer.predict(test_x)

print(train_x[0])
print(train_predict[0])
print(test_x[0])
print(test_predict[0])

strict_train, strict_test = do_estimate(train_y, train_predict, 0), do_estimate(test_y, test_predict, 0)
hl_train, hl_test = do_estimate(train_y, train_predict, 0.5), do_estimate(test_y, test_predict, 0.5)
len_train, len_test = do_estimate(train_y, train_predict, 1), do_estimate(test_y, test_predict, 1)

print("Strict", strict_train, strict_test)
print("Half lenient", hl_train, hl_test)
print("Lenient", len_train, len_test)

with open(config.stat_file_name, "a") as file:
    print(strict_train, strict_test, config.iterations, "strict", file=file, sep=",")
    print(hl_train, hl_test, config.iterations, "halflenient", file=file, sep=",")
    print(len_train, len_test, config.iterations, "lenient", file=file, sep=",")

diff = time.time() - now
print("=" * 20)
print("DONE IN %d minutes %d seconds" % (diff // 60, diff % 60))
