import time
import shutil
import os
import datetime
from xml.etree import ElementTree as ET


def xml_parser(xml_file):
    tree = ET.parse(xml_file)
    table = tree.getroot()
    return table


def backup_data():
    backup_dir = time.strftime('%Y-%m-%d_%T', time.localtime(time.time()))
    shutil.move('../data/', '../backup/' + backup_dir)
    os.mkdir('../data/')
    os.mkdir('../data/customers')
    os.mkdir('../data/payment')
    os.mkdir('../data/goods')
    os.mkdir('../data/inventory')
    os.mkdir('../data/temp')
    os.mkdir('../data/jd_orders')
    os.mkdir('../data/taobao_orders')


def datetime_earlier(d, hours=0, days=0):
    time_delta = datetime.timedelta(hours=hours, days=days)
    day = d - time_delta
    date_to = datetime.datetime(day.year, day.month, day.day, day.hour, day.minute, day.second)
    return date_to


def datetime_later(d, hours=0, days=0):
    time_delta = datetime.timedelta(hours=hours, days=days)
    day = d + time_delta
    date_to = datetime.datetime(day.year, day.month, day.day, day.hour, day.minute, day.second)
    return date_to


