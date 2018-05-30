from datetime import datetime
from numpy import around


class Estimator:
    def __init__(self, metric: callable, metric_name: str, stat_file_name: str, do_round: bool = False, do_class: bool = False):
        self.__metric = metric
        self.__metric_name = metric_name
        self.__stat_file_name = stat_file_name

        self.__file = open(stat_file_name, "a")
        self.__do_round = do_round
        self.__do_class = do_class

    def __del__(self):
        self.close()

    def close(self):
        self.__file.close()

    def estimate(self, expected, predict):
        print(expected[:5].flatten())
        print(predict[:5].flatten())
        exp = expected.flatten() if self.__do_class else expected
        pred = predict.flatten() if self.__do_class else predict
        if self.__do_round:
            return self.__metric(around(exp), around(pred))
        return self.__metric(exp, pred)

    def estimate_all(self, train_y, train_predict, test_y, test_predict):
        train_score = self.estimate(train_y, train_predict)
        test_score = self.estimate(test_y, test_predict)
        return train_score, test_score

    def estimate_all_and_save(self, train_y, train_predict, test_y, test_predict, iterations):
        train_score, test_score = self.estimate_all(train_y, train_predict, test_y, test_predict)
        print("Train score: %f test score: %f" % (train_score, test_score))
        if iterations > 0:
            print("%s,%d,%f,%f,%s" % (datetime.now(), iterations, train_score, test_score, self.__metric_name),
                  file=self.__file)
