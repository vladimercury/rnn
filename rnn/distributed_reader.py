import csv


def compute_chunk_data(max_lines_no: int, max_chunk_size: int, max_error: float = 0.01):
    chunk_size = min(max_chunk_size, max_lines_no)
    chunk_number = max_lines_no // chunk_size
    lines_no = chunk_number * chunk_size
    while (max_lines_no - lines_no) / max_lines_no > max_error:
        chunk_number += 1
        chunk_size = max_lines_no // chunk_number
        lines_no = chunk_number * chunk_size
    return chunk_size, chunk_number


class DistributedReader:
    """
        Arguments:
            input_file_name: string
                Name of the file to read data from
            lines_number: int
                Number of the data lines in the file
            max_chunk_size: int, default 800
                Max allowed size of the chunk
            exclude_first_row: bool, default True
                If it need to exclude first (header) row
    """
    def __init__(self, input_file_name: str, lines_number: int, max_chunk_size: int = 800,
                 exclude_first_row: bool = True):
        self.__input_file_name = input_file_name

        self.__chunk_size, self.__chunk_no = compute_chunk_data(lines_number, max_chunk_size)

        self.__file = open(self.__input_file_name, "r")
        self.__reader = csv.reader(self.__file)
        if exclude_first_row:
            next(self.__reader)

        self.__current_chunk_index = 0

    def __del__(self):
        self.close()

    def close(self):
        if self.__file and not self.__file.closed:
            self.__file.close()

    def next_chunk(self):
        if self.__current_chunk_index < self.__chunk_no:
            chunk = list()
            counter = 0
            for row in self.__reader:
                counter += 1
                chunk.append(row)
                if counter >= self.__chunk_size:
                    break
            self.__current_chunk_index += 1
            return chunk
        return None

    def extra_data(self):
        return [row for row in self.__reader]

    def chunks(self):
        chunk = self.next_chunk()
        while chunk is not None:
            yield chunk
            chunk = self.next_chunk()

    def stat(self):
        return self.__current_chunk_index, self.__chunk_no
