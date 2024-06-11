try:
    import os
    import json
    import re
    import csv
    import time
    from datetime import datetime
    from tqdm import tqdm
    from google_sheets_utils.buid import GoogleSheets
    from google_sheets_utils.text_handler import all_to_low_and_del_spc as to_low
    from openai import OpenAI
    from params import *
    from functions import read_json, write_json, read_file_lines, generate_bullets_process
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to continue...")
    raise


def app_start():
    try:
        while True:
            print(HELLO_MESSAGE)
            do = input('Введите действие: ').strip()

            while True:
                if do in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                    break
                else:
                    print('Такого действия нет')
                    do = input('Введите действие: ').strip()

            if do == '1':
                shop_name = input('Введите название магазина: ').strip().lower()
                row_start = input('С какой строки начать (если оставить поле пустым или начать ввести < 2, то бот начнет со 2 строки): ').strip()
                if row_start == '':
                    row_start = 2
                elif int(row_start) < 2:
                    row_start = 2
                else:
                    row_start = int(row_start)

                try:
                    row_end = int(input('По какую включительно (не обязательно): ').strip())
                except ValueError:
                    row_end = None
                shops_info = read_json(INFO.get('db_paths').get('shops_info_path'))

                match_found = False
                for shop_dict in shops_info:
                    if shop_dict['shop_name'] == shop_name:
                        report = generate_bullets_process(shop_dict, row_start, row_end)
                        match_found = True
                        print(
                            f'Обработан магазин: {shop_name}\n'
                            f'Обработано товаров: {report.get("title_processed")}\n'
                            f'Создано буллетов: {report.get("bullets")}\n'
                            f'Потрачено токенов: {report.get("tokens")}\n'
                        )
                        break
                if not match_found:
                    print('Магазин не найден')
                print()

            elif do == '2':
                shops_info = read_json(INFO.get('db_paths').get('shops_info_path'))
                for shop_dict in shops_info:
                    print('Name: ' + shop_dict['shop_name'])
                    print('Table ID: ' + shop_dict['table_id'])
                    print('Worksheet: ' + shop_dict['worksheet'])
                    print('Columns: ' + str(shop_dict['columns']))
                    print('Title column: ' + shop_dict['title_column'])
                    print()

                input('Нажмите Enter для выхода...')

            elif do == '3':
                shops_info = read_json(INFO.get('db_paths').get('shops_info_path'))
                google_creds = read_json(INFO.get('creds_paths').get('google_creds_path'))

                print(f'Перед добавлением магазина дайте доступ к почте - {google_creds.get("client_email")}')
                shop_name = input('Введите название магазина (регистр опускается): ').strip().lower()
                for shop_dict in shops_info:
                    if shop_dict['shop_name'] == shop_name:
                        print('Магазин уже существует')
                        break

                else:
                    table_id = input('Введите ID таблицы: ').strip()
                    worksheet = input('Введите название листа, в котором будет работать бот: ')
                    title_column = input('Введите название столбца, в котором находятся тайтлы: ').strip()
                    columns = []
                    print()
                    print('Вводите названия столбцов, куда нужно будет вводить готовые буллеты.\n'
                          'Кол-во указанных столбцов будет равняться кол-ву сгенерированных буллетов.\n'
                          'Введите "q", чтобы закончить ввод.')
                    while True:
                        column_name = input('Введите название столбца куда будут внесены буллеты: ').strip()
                        if column_name == 'q':
                            break
                        columns.append(column_name)

                    shop_dict = {
                        'shop_name': shop_name,
                        'table_id': table_id,
                        'worksheet': worksheet,
                        'columns': columns,
                        'title_column': title_column
                    }
                    shops_info.append(shop_dict)
                    write_json(INFO.get('db_paths').get('shops_info_path'), shops_info)
                    print('Магазин добавлен')
                    print()

            elif do == '4':
                shops_info = read_json(INFO.get('db_paths').get('shops_info_path'))

                shop_name = input('Введите название магазина: ').strip().lower()

                for shop_dict in shops_info:
                    if shop_dict['shop_name'] == shop_name:
                        shops_info.remove(shop_dict)
                        break

                write_json(INFO.get('db_paths').get('shops_info_path'), shops_info)
                print('Магазин удален')
                print()

            elif do == '5':
                while True:
                    black_list = read_json(INFO.get('db_paths').get('black_list_path'))
                    black_word = input('Введите запрещенное слово ("q" - выход): ').strip().lower()
                    if black_word == 'q':
                        break
                    if black_word in black_list:
                        print('Запрещенное слово уже есть в списке')
                    else:
                        black_list.append(black_word)
                        write_json(INFO.get('db_paths').get('black_list_path'), black_list)
                        print('Запрещенное слово добавлено')
                        print()

            elif do == '6':
                while True:
                    black_list = read_json(INFO.get('db_paths').get('black_list_path'))
                    print(
                        f'Занесите запрещенные слова в файл по пути {INFO.get("templates_paths").get("append_template")}\n'
                        'Каждое новое слово, должно начинаться с новой строки'
                    )
                    approve = input('После занесения нажмите Enter ("q" - выход): ').strip().lower()
                    if approve == 'q':
                        break
                    new_black_words = [word.replace('\n', '') for word in
                                       read_file_lines(INFO.get("templates_paths").get('append_template'))]

                    for word in new_black_words:
                        if word not in black_list:
                            black_list.append(word)

                    write_json(INFO.get('db_paths').get('black_list_path'), black_list)
                    print('Запрещенные слова добавлены')
                    print()

            elif do == '7':
                while True:
                    black_list = read_json(INFO.get('db_paths').get('black_list_path'))
                    black_word = input('Введите запрещенное слово для удаления ("q" - выход): ').strip().lower()
                    if black_word == 'q':
                        break
                    if black_word not in black_list:
                        print('Запрещенное слово не найдено в списке')
                    else:
                        black_list.remove(black_word)
                        write_json(INFO.get('db_paths').get('black_list_path'), black_list)
                        print('Запрещенное слово удалено')
                        print()

            elif do == '8':
                while True:
                    black_list = read_json(INFO.get('db_paths').get('black_list_path'))
                    print(
                        f'Занесите запрещенные слова в файл по пути {INFO.get("templates_paths").get("delete_template")}\n'
                        'Каждое новое слово, должно начинаться с новой строки'
                    )
                    approve = input('После занесения нажмите Enter ("q" - выход): ').strip().lower()
                    if approve == 'q':
                        break
                    new_black_words = [word.replace('\n', '') for word in
                                       read_file_lines(INFO.get("templates_paths").get('delete_template'))]

                    for word in new_black_words:
                        if word in black_list:
                            black_list.remove(word)

                    write_json(INFO.get('db_paths').get('black_list_path'), black_list)
                    print('Запрещенные слова удалены')
                    print()

            elif do == '9':
                break
    except Exception as error:
        print(error)
        input('Нажмите Enter для выхода')


if __name__ == '__main__':
    app_start()
