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
    from moduls import GPT
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to continue...")
    raise


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def read_file_lines(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()


def clear_file(file_path):
    with open(file_path, 'w') as f:
        f.truncate()


def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def write_csv(file_path, data):
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def collect_data_to_csv(data):
    max_length = max(len(lst) for lst in data)
    for lst in data:
        while len(lst) < max_length:
            lst.append([""])
    combined = [sum((lst[i] for lst in data), []) for i in range(max_length)]
    file_name = INFO.get('db_paths').get('processed') + f'bullets {datetime.now().day}.{datetime.now().month} {datetime.now().hour}-{datetime.now().minute}.csv'
    write_csv(file_name, combined)
    return file_name


def remove_forbidden_words(text, forbidden_words_path=INFO.get('db_paths').get('black_list_path')):
    forbidden_words = read_json(forbidden_words_path)
    pattern = '|'.join(re.escape(word) for word in forbidden_words)
    return re.sub(pattern, '', text, flags=re.IGNORECASE)


def generate_bullets(gpt, titles, qty_bullets, row_start, promt_path=INFO.get('templates_paths').get('promt_template')):
    promt_body = read_file(promt_path)
    model = INFO.get('gpt_model')
    client = gpt.authorize_openai()
    result = {'bullets': {}, 'tokens': 0}
    try:
        for title in tqdm(titles, desc='Генерация буллетов'):
            promt_header = f'Создай {qty_bullets} буллетов для товарв "{title}". Используй следующие параметры:'
            promt = f'{promt_header}\n{promt_body}'
            response = gpt.req_to_gpt(client=client, model=model, prompt=promt)
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens

            bullets: dict = json.loads(content)

            col = 0
            for bullet in bullets.values():
                if result['bullets'].get(col) is None:
                    result['bullets'][col] = [[bullet]]
                else:
                    result['bullets'][col].append([bullet])
                col += 1
                if col > qty_bullets - 1:
                    break
            result['tokens'] += tokens
    finally:
        all_bullets = []
        for bullets in result['bullets'].values():
            all_bullets.append(bullets)
        file_name = collect_data_to_csv(all_bullets)

        print(f'К сожалению возникла ошибка при генерации.\n'
              f'Буллеты, которые успели сгенерироваться находятся в файле {file_name}.\n'
              f'При необходимости их можно перенести в таблицу вручную.\n'
              f''
              f'Всего потрачено токенов: {result["tokens"]}\n'
              f'Успешно сгенерировано: {sum(len(bul) for bul in result["bullets"].values())} буллетов.\n'
              f'Генерация начиналась со строки: {row_start}.')

    return result


def generate_bullets_process(
        shop_dict, row_start, row_end, google_creds_path=INFO.get('creds_paths').get('google_creds_path')
):
    shop_name = shop_dict.get('shop_name')
    table_id = shop_dict.get('table_id')
    worksheet = shop_dict.get('worksheet')
    columns = shop_dict.get('columns')
    title_column = shop_dict.get('title_column')

    google_sheet = GoogleSheets(google_creds_path)
    all_data_from_sheet = google_sheet.get_all_info_from_sheet(table_id, worksheet)
    column_row = [to_low(elem) for elem in all_data_from_sheet[0]]
    columns_indices = []
    title_index = column_row.index(to_low(title_column))
    for column in columns:
        columns_indices.append(
            {
                'col': column_row.index(to_low(column)) + 1,
                'row': row_start
            }
        )

    titles = [elem[title_index] for elem in all_data_from_sheet[row_start - 1:row_end]]

    gpt = GPT()
    bullets = generate_bullets(gpt, titles, len(columns), row_start)

    for col, bullet_list in bullets['bullets'].items():
        columns_indices[col]['data'] = bullet_list

    status = google_sheet.update_sheet_by_indices(
        spreadsheet=table_id, worksheet=worksheet, indices=columns_indices
    )

    return {
        'shop_name': shop_name,
        'title_processed': len(titles),
        'bullets': len(titles) * len(columns),
        'tokens': bullets.get('tokens'),
        'update_sheet_status': status
    }


