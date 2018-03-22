import logging
import os

from bin.config import Config

config = Config(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/conf/config.ini')

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d] %(message)s',
                    datefmt='%d %b %Y %H:%M:%S')
