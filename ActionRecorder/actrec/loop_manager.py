# region Imports
from collections import defaultdict
# endregion

# Глобальные переменные для управления циклами
loop_table = {}
loop_iterator = defaultdict(int)
loop_size = {}


def reset_loops():
    """Сброс всех данных о циклах"""
    global loop_table, loop_iterator, loop_size
    loop_table.clear()
    loop_iterator.clear()
    loop_size.clear()


def setup_loop(start_macro, end_macro, loop_data, start_index):
    """Настройка цикла"""
    loop_table[end_macro.id] = start_macro.id
    loop_size[start_macro.id] = start_index
    loop_iterator[start_macro.id] = 0

    if loop_data.get('StatementType') == 'count':
        # DEPRECATED: support old count loop macros
        loop_iterator[start_macro.id] = loop_data.get("Startnumber", 0)


def get_loop_info(macro_id):
    """Получение информации о цикле"""
    return {
        'table': loop_table.get(macro_id),
        'iterator': loop_iterator.get(macro_id, 0),
        'size': loop_size.get(loop_table.get(macro_id), 0)
    }


def increment_loop_iterator(start_id):
    """Увеличение итератора цикла"""
    loop_iterator[start_id] += 1


def reset_loop_iterator(start_id):
    """Сброс итератора цикла"""
    loop_iterator[start_id] = 0

