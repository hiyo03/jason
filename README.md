# Notion to Slack Task Notifier

Notionのタスクデータベースから期限が近いタスクと期限切れタスクを取得し、Slackに担当者のメンション付きで通知するPythonスクリプトです。  
進捗状況はNotionのロールアップ型プロパティから取得し、％表示で通知します。

---

## 機能

- Notionデータベースから「期限が今日〜3日後まで」のタスクを取得しSlack通知  
- 「期限が過ぎている」タスクも別途Slack通知  
- 担当者名をSlackユーザーIDにマッピングしてメンションを付ける  
- 進捗状況（ロールアップ数値）を通知に含める  

---

## 必要環境

- Python 3.7以上  
- `notion-client`  
- `slack_sdk`  
- `python-dotenv`  

```bash
pip install notion-client slack_sdk python-dotenv
