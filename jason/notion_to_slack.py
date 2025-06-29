import os
import datetime
from dotenv import load_dotenv
from slack_sdk import WebClient
from notion_client import Client

# .envファイルから環境変数読み込み
load_dotenv()

# APIクライアント初期化
notion = Client(auth=os.getenv("NOTION_TOKEN"))
slack = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# 担当者名 → SlackユーザーID のマップ（必要に応じて追加）
USER_MAP = {
    "おおくぼひおり": "U0944FG0MU0",
    "yuika": "U0939JVQ6D9",
    "KAWAMURATamaki": "U0944FJ4QHW"
}

# 締切が今日〜3日後のタスクを取得
def get_upcoming_tasks():
    today = datetime.datetime.utcnow().date().isoformat()
    three_days = (datetime.datetime.utcnow() + datetime.timedelta(days=3)).date().isoformat()

    response = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "and": [
                    {"property": "期限", "date": {"on_or_after": today}},
                    {"property": "期限", "date": {"on_or_before": three_days}},
                ]
            }
        }
    )
    return response["results"]

# 締切が過ぎているタスクを取得
def get_overdue_tasks():
    today = datetime.datetime.utcnow().date().isoformat()
    response = notion.databases.query(
        **{
            "database_id": DATABASE_ID,
            "filter": {
                "property": "期限",
                "date": {"before": today}
            }
        }
    )
    return response["results"]

# Slack通知送信
def send_task_notifications(tasks, is_overdue=False):
    for task in tasks:
        props = task["properties"]

        # タスク名取得（空なら"無題"）
        name = props["タスク名"]["title"][0]["text"]["content"] if props["タスク名"]["title"] else "無題"
        
        # 締切日
        date = props["期限"]["date"]["start"]

        # 進捗状況（ロールアップ型・数値として取得）
        progress = props.get("進捗状況", {}).get("rollup", {}).get("number", None)
        progress_str = f"進捗：{int(progress)}%" if progress is not None else "進捗：不明"

        # 担当者
        user = props["担当者"]["people"][0]["name"] if props["担当者"]["people"] else "未割当"
        slack_user = USER_MAP.get(user, "")
        
        # 通知メッセージの種別
        status = "締切が過ぎています" if is_overdue else "期限が近いです"
        
        # Slack送信内容
        slack_msg = f"{status}：タスク「{name}」（{date}）{progress_str}\n{f'<@{slack_user}>' if slack_user else user}"
        slack.chat_postMessage(channel=CHANNEL_ID, text=slack_msg)

# メイン処理
if __name__ == "__main__":
    upcoming_tasks = get_upcoming_tasks()
    overdue_tasks = get_overdue_tasks()

    if upcoming_tasks:
        send_task_notifications(upcoming_tasks)
    if overdue_tasks:
        send_task_notifications(overdue_tasks, is_overdue=True)

    if not upcoming_tasks and not overdue_tasks:
        print("通知すべきタスクはありません")
