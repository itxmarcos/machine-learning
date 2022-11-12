import logging

logger = logging.getLogger(__name__) # Create a custom logger

################################
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s::: %(message)s', datefmt='%d-%b-%y %H:%M:%S')
str = 'wawawiwa'
logging.debug(f'My string is {str}')

################################
a = 5
b = 0
try:
  c = a / b
except Exception as e:
  logging.exception("Exception occurred", exc_info=True)
