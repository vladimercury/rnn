from rnn import Config, CSVRowParser, DistributedReader, DistributedTrainer, Estimator

config = Config("config.yaml")

train_lines_no = (config.input_file_lines_no * config.train_set_percentage) // 100
reader = DistributedReader(input_file_name=config.input_file_name, lines_number=train_lines_no,
                           max_chunk_size=config.max_chunk_size)
parser = CSVRowParser(config=config.input_vector)
trainer = DistributedTrainer(model_class=config.model_type, row_shape=config.input_vector_length,
                             model_file_path=config.model_file_name, look_back_shift=config.look_back_shift,
                             epoch_number=config.iterations)
estimator = Estimator(metric=config.metric_type, metric_name=config.metric_type_name,
                      stat_file_name=config.stat_file_name, do_round=False)

for chunk in reader.chunks():
    print("\n NEXT CHUNK \n")
    data = parser.batch_parse(chunk)
    train_x, train_y = trainer.train(data)

trainer.save()

test_x, test_y = trainer.prepare_x_y(parser.batch_parse(reader.extra_data()))
train_predict = trainer.predict(train_x)
test_predict = trainer.predict(test_x)

estimator.estimate_all_and_save(train_y=trainer.inverse_transform(train_y),
                                train_predict=trainer.inverse_transform(train_predict),
                                test_y=trainer.inverse_transform(test_y),
                                test_predict=trainer.inverse_transform(test_predict),
                                iterations=config.iterations)
