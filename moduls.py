from __init__ import *
from params import *
import functions


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
