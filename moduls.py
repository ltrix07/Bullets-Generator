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
    import functions
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to continue...")
    raise


class GPT:
    def __init__(self, key_path=INFO.get('creds_paths').get('api_key_path')):
        self.key_path = key_path

    def authorize_openai(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            api_key = functions.read_file(self.key_path)
            if not api_key:
                raise ValueError(
                    f'API ключ не найден. Пожалуйста занесите его в файл {self.key_path} или в переменную окружения '
                    f'OPENAI_API_KEY'
                )

        return OpenAI(api_key=api_key)

    @staticmethod
    def req_to_gpt(client, model, prompt):
        return client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
