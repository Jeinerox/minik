import logging
import os

def my_logger(file, name, level):
	os.makedirs(os.path.dirname(file), exist_ok=True)

	logger = logging.getLogger(name)
	logger.setLevel(level)

	handler = logging.FileHandler(file, mode='a')
	formatter = logging.Formatter('[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)

	return logger