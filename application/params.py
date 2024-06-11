INFO = {
    'version': '0.0.1',
    'gpt_model': 'gpt-3.5-turbo-0125',
    'creds_paths': {
        'google_creds_path': './creds/google_creds.json',
        'api_key_path': 'creds/openai_api_key.txt'
    },
    'db_paths': {
        'black_list_path': './db/words_black_list.json',
        'shops_info_path': './db/shops_info.json',
        'processed': './db/'
    },
    'templates_paths': {
        'append_template': './templates/append_to_black_list.txt',
        'delete_template': './templates/delete_from_black_list.txt',
        'promt_template': './templates/promt.txt'
    }
}

HELLO_MESSAGE = \
f"""
Я программа для создания буллетов. v{INFO['version']}
Какие действия вы хотите сделать?

    1. Создать буллеты
    2. Вывести список магазинов
    2. Добавить новую таблицу
    3. Удалить таблицу
    4. Добавить запрещенное слово
    5. Добавить запрещенные слова (списком)
    6. Удалить запрещенное слово
    7. Удалить запрещенные слова (списком)
    
    8. Выйти
    
    
"""