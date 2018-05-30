from rnn import Config, CSVRowParser, DistributedReader, DistributedTrainer, Estimator
import time

now = time.time()
config = Config("config-v2.yaml")

train_lines_no = (config.input_file_lines_no * config.train_set_percentage) // 100
reader = DistributedReader(input_file_name=config.input_file_name, lines_number=train_lines_no,
                           max_chunk_size=config.max_chunk_size)
parser = CSVRowParser(config=config.input_vector)
trainer = DistributedTrainer(model_class=config.model_type, row_shape=config.input_vector_length,
                             model_file_path=config.model_file_name, look_back_shift=config.look_back_shift,
                             epoch_number=config.iterations, verbose_level=3)
estimator = Estimator(metric=config.metric_type, metric_name=config.metric_type_name,
                      stat_file_name=config.stat_file_name, do_round=config.round, do_class=config.classification_score)

for chunk in reader.chunks():
    print("\nCHUNK %d of %d\n" % reader.stat())
    data = parser.batch_parse_pc_spec(chunk)
    train_x, train_y = trainer.train(data)

trainer.save()

parsed_test = parser.batch_parse(reader.extra_data())
test_x, test_y = trainer.prepare_x_y(parsed_test)
train_predict = trainer.predict(train_x)
test_predict = trainer.predict(test_x)

if config.transform:
    print(estimator.estimate_all_and_save(train_y=trainer.inverse_transform(train_y),
                                    train_predict=trainer.inverse_transform(train_predict),
                                    test_y=trainer.inverse_transform(test_y),
                                    test_predict=trainer.inverse_transform(test_predict), iterations=config.iterations))
else:
    print(estimator.estimate_all_and_save(train_y=train_y.flatten(), train_predict=train_predict.flatten(),
                                          test_y=test_y.flatten(), test_predict=test_predict.flatten(),
                                          iterations=config.iterations))

diff = time.time() - now
print("=" * 20)
print("DONE IN %d minutes %d seconds" % (diff // 60, diff % 60))
