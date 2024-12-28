import pandas as pd
import os
from datetime import datetime

class FileAppender:
    """
    Appends if file existing new data to the file, otherwise creates new one.
    """

    @staticmethod
    def append_data_as_csv(data, name: str, current_datetime: datetime):
        """
        Converts data to DataFrame, checks does file exist and saves data.
        File has name in format {name}_{current_datetime}.csv
        File is saving in current folder.
        :param data: Data to be saved.
        :param name: Name of file without extension.
        :param current_datetime: Current date of file.
        """
        data_df = pd.DataFrame(data)
        is_file_exists = os.path.isfile(f'data/{name}.csv')

        if current_datetime is None:
            current_datetime = datetime.now()

        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        data_df.to_csv(f'data/{name}_{formatted_datetime}.csv', mode='a', header=not is_file_exists, index=False)