# Activity DB モジュール

活動情報をSupabase（PostgreSQL）で管理するモジュール

## 📋 概要

日々の開発・学習活動を記録し、各種SNS投稿の元データとして管理します。

## 🗄️ データ構造

```json
{
    "id": "uuid-string",
    "timestamp": "2025-01-12T10:30:00+09:00",
    "content": "活動内容の本文",
    "created_at": "2025-01-12T10:30:00+09:00"
}
```

## 🚀 セットアップ

### 1. Supabaseプロジェクト作成

1. [Supabase](https://supabase.com/)にアクセス
2. 新規プロジェクト作成
3. Project URLとanon public keyを取得

### 2. テーブル作成

Supabase Web UIの「SQL Editor」で以下を実行:

```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activities_timestamp ON activities(timestamp DESC);
```

### 3. 環境変数設定

プロジェクトルートの`.env`ファイルに追加:

```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 4. 依存ライブラリインストール

```bash
pip install supabase python-dotenv
```

## 📝 使い方

### 活動を追加

```bash
python add_activity.py "ClaudeCodeでDB設計完了"
```

オプション:
```bash
# タイムスタンプ指定
python add_activity.py "活動内容" --timestamp "2025-01-12T10:30:00"
```

### 活動一覧表示

```bash
# 最新10件表示
python list_activities.py

# 件数指定
python list_activities.py --limit 20

# 最新1件のみ表示
python list_activities.py --latest

# オフセット指定（ページング）
python list_activities.py --limit 10 --offset 10
```

### 古いデータ削除

```bash
# 統計情報のみ表示
python cleanup.py --stats-only

# 90日以前のデータを削除（確認あり）
python cleanup.py --days 90

# 確認なしで削除
python cleanup.py --days 90 --yes
```

## 🐍 Pythonから使用

```python
from activity_db.db import ActivityDB

# 初期化
db = ActivityDB()

# 活動追加
activity = db.add_activity("新しい活動内容")
print(f"追加されたID: {activity['id']}")

# 最新取得
latest = db.get_latest()
print(f"最新: {latest['content']}")

# ID指定取得
activity = db.get_activity("uuid-here")

# 一覧取得
activities = db.list_activities(limit=10)
for act in activities:
    print(f"[{act['timestamp']}] {act['content']}")

# 総数取得
count = db.count_activities()
print(f"総数: {count}")
```

## 🧹 メンテナンス

### 定期的なクリーンアップ

容量管理のため、定期的に古いデータを削除してください:

```bash
# 3ヶ月（90日）以前のデータを削除
python cleanup.py --days 90 --yes
```

### VACUUM実行

大量削除後は、Supabase Web UIで以下を実行して容量を解放:

```sql
VACUUM FULL activities;
```

または、自動VACUUM を有効化:

```sql
ALTER TABLE activities SET (autovacuum_enabled = true);
```

## 📊 データベース統計

```bash
python cleanup.py --stats-only
```

出力例:
```
📊 データベース統計:
============================================================
総件数: 150
最古データ: 2024-10-15 10:30:00
最新データ: 2025-01-12 15:45:00
データ期間: 89日
============================================================
```

## 🔧 テスト実行

```bash
# db.pyの動作確認
python db.py
```

## 📁 ファイル構成

```
activity_db/
├── __init__.py           # モジュール初期化
├── db.py                 # DB操作コア
├── add_activity.py       # 活動追加CLI
├── list_activities.py    # 活動一覧CLI
├── cleanup.py            # データクリーンアップ
└── README.md             # 本ドキュメント
```

## ⚠️ 注意事項

1. **環境変数**: `.env`ファイルは絶対にGitにコミットしないでください
2. **容量管理**: Supabase無料枠は500MBです。定期的にクリーンアップを実行してください
3. **VACUUM**: 大量削除後は手動でVACUUMを実行することを推奨します

## 🐛 トラブルシューティング

### 接続エラー

```
ValueError: SUPABASE_URLとSUPABASE_KEYを.envに設定してください
```

→ `.env`ファイルに正しくSupabase認証情報を設定してください

### テーブルが存在しない

```
❌ テーブルが存在しません
```

→ Supabase Web UIで CREATE TABLE を実行してください

## 📚 参考リンク

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL VACUUM Documentation](https://www.postgresql.org/docs/current/sql-vacuum.html)
- [容量管理の参考記事](https://zenn.dev/shimotani/articles/45206b9aacdad7)
