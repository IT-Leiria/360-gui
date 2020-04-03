
import logging


def setup_logging(log_filename, log_level, log_format):

    logging.basicConfig(level=log_level,
                        filename=log_filename,
                        format=log_format,
                        filemode='w+')
