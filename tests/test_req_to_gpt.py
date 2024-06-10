from functions import req_to_gpt, authorize_openai


client = authorize_openai('../creds/openai_api_key.txt')


def test_req_to_gpt():
    print(req_to_gpt(client, 'gpt-3.5-turbo-0125', 'hello'))


test_req_to_gpt()

