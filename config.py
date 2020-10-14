# -*- coding: utf-8 -*-

from enum import Enum

db_file = "database.vdb"
token = 'token here'


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"  # Идентификатор товара
    S_ENTER_GOODS_ID = "2"  # Идентификатор товара
    S_PERIOD_START = "3"  # Дата начала периода
    S_PERIOD_END = "4"  # Дата окончания периода
    S_END = "5"  # Окончание диалога
