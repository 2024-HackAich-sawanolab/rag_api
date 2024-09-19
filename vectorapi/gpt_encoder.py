import openai
from dotenv import load_dotenv
from os.path import join, dirname
import os


def gpt_encode(text: str) -> str:
    dotenv_path = join(dirname(__file__), ".env")
    load_dotenv(dotenv_path, verbose=True)
    openai_api_key = os.environ.get('OPENAI_API_KEY')

    client = openai.Client()
    # envの一覧を表示
    client.api_key = openai_api_key
    prompts = 'あなたはRAGに入れるためのベクトルデータ作成の仕事をしています．これから入力する文章に関して重要であるキーワードを抜き出してください．また，キーワード以外の文章を出力で表示しないでください．\n入力: ' + text
    print("prompts ", prompts)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "",
            },
            {"role": "user", "content": prompts},
        ],
    )
    message_object = completion
    print("message_object ", message_object)
    return "hogehoge"
