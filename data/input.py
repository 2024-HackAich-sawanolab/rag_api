import csv
import requests
import json
import uuid

# 入力CSVファイルの名前を指定
csv_file = 'output.csv'

# POSTリクエストを送信するURLを指定
url = 'http://localhost:8889/v1/collections/my_collection/upsert'

# ヘッダー情報を指定
headers = {
    "Content-Type": "application/json"
}

# CSVファイルを読み込み、各行についてPOSTリクエストを送信
with open(csv_file, 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        id_value = row['管理NO']
        inquiry = row['問合せ内容']
        answer = row['回答内容']

        # "input"フィールドを作成
        input_text = f"{inquiry}: {answer}"

        # ペイロードを作成
        uuid_4 = str(uuid.uuid4())
        payload = {
            "id": uuid_4,
            "metadata": {"key": "value"},
            "input": input_text
        }

        # POSTリクエストを送信
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # レスポンスのステータスコードをチェック
        if response.status_code == 200:
            print(f"ID {uuid_4} のデータを正常に送信しました。")
        else:
            print(f"ID {uuid_4} のデータ送信に失敗しました。ステータスコード: {response.status_code}")
            print(f"レスポンス内容: {response.text}")
