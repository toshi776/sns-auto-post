# 作業再開手順

## 現在の状況

### 完了した作業
✅ X投稿文生成プロンプトを更新（140文字検索最適化対応）
✅ Note記事生成プロンプトを更新（casual寄り、2000-4000文字）
✅ Qiita/Zenn技術記事生成プロンプトを作成
✅ Activity DBのID形式を5桁数字に変更（UUID → 00001形式）
✅ プロンプト集をPROMPTS.mdに保存

### 次のステップ

#### 1. 環境設定（自宅で実施）

.envファイルを作成してください：

```bash
cd /home/toshi776/projects/sns-auto-post
cp .env.example .env
```

以下の情報を.envに設定：
- SUPABASE_URL
- SUPABASE_KEY
- GEMINI_API_KEY
- X API認証情報（X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, X_BEARER_TOKEN）
- Note.com認証情報（NOTE_EMAIL, NOTE_PASSWORD）

#### 2. Supabaseデータベースのマイグレーション

Supabase Web UI > SQL Editorで以下を実行：

```sql
-- Step 1: 新テーブル作成
CREATE TABLE activities_new (
    id VARCHAR(5) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activities_new_timestamp ON activities_new(timestamp DESC);

-- Step 2: 既存データ移行（00001から採番）
INSERT INTO activities_new (id, timestamp, content, created_at)
SELECT
    LPAD(ROW_NUMBER() OVER (ORDER BY timestamp ASC)::TEXT, 5, '0') as id,
    timestamp,
    content,
    created_at
FROM activities
ORDER BY timestamp ASC;

-- Step 3: データ確認
SELECT * FROM activities_new ORDER BY id ASC LIMIT 10;
SELECT COUNT(*) FROM activities;
SELECT COUNT(*) FROM activities_new;

-- Step 4: テーブル入れ替え（データ確認後）
ALTER TABLE activities RENAME TO activities_old;
ALTER TABLE activities_new RENAME TO activities;
```

#### 3. 活動データの登録とX投稿

以下のコマンドを実行：

```bash
cd /home/toshi776/projects/sns-auto-post

# 1. 昨日の活動をDBに登録
python3 activity_db/add_activity.py "昨日の活動: PythonでSNS自動投稿システムを開発。Gemini APIを使ってX投稿文とNote記事を自動生成し、tweepy経由でX投稿、Selenium + undetected-chromedriver でnote.comへの自動投稿を実装。活動データはSupabaseで管理。X投稿は140文字検索最適化、Note記事はcasual寄りの2000-4000文字で作成。技術スタック: Python3, Gemini API (gemini-2.0-flash-exp), tweepy, Selenium, Supabase"

# 2. 登録された活動を確認
python3 activity_db/list_activities.py

# 3. 最新の活動からX投稿文を生成
cd x_platform
python3 generate_x.py "$(python3 -c 'import sys; sys.path.insert(0, ".."); from activity_db.db import ActivityDB; db = ActivityDB(); activity = db.get_latest(); print(activity["content"])')"

# または、IDを指定して生成
# python3 generate_x.py "$(python3 -c 'import sys; sys.path.insert(0, ".."); from activity_db.db import ActivityDB; db = ActivityDB(); activity = db.get_activity("00001"); print(activity["content"])')"

# 4. X投稿文が良ければ、実際に投稿
# python3 post_x.py "生成されたX投稿文をここにコピー"
```

#### より簡単な方法（推奨）

1. **活動登録**
```bash
python3 activity_db/add_activity.py "活動内容"
```

2. **最新活動のIDを確認**
```bash
python3 activity_db/list_activities.py
```

3. **X投稿文生成（IDを使用）**
```bash
# 例: ID 00001 の活動から生成
python3 -c "
import sys
sys.path.insert(0, '.')
from activity_db.db import ActivityDB
from x_platform.generate_x import generate_x_post

db = ActivityDB()
activity = db.get_activity('00001')  # IDを指定
post_text = generate_x_post(activity['content'])
print(post_text)
"
```

4. **X投稿**
```bash
python3 x_platform/post_x.py "生成された投稿文"
```

## ファイル構成

```
sns-auto-post/
├── .env                          # 環境変数（自宅で作成）
├── .env.example                  # 環境変数のサンプル
├── PROMPTS.md                    # プロンプト集
├── migrate_id_format.md          # DBマイグレーション手順
├── generate_technical_article.py # Qiita/Zenn記事生成
├── activity_db/
│   ├── db.py                    # DB操作（5桁ID対応済み）
│   ├── add_activity.py          # 活動追加
│   └── list_activities.py       # 活動一覧
├── x_platform/
│   ├── generate_x.py            # X投稿文生成（更新済み）
│   └── post_x.py                # X投稿
└── note_platform/
    ├── generate_note.py         # Note記事生成（更新済み）
    └── post_note.py             # Note投稿
```

## トラブルシューティング

### モジュールが見つからない場合
```bash
pip3 install -r requirements.txt
```

### .envが読み込まれない場合
```bash
# .envファイルがプロジェクトルートにあることを確認
ls -la .env

# パーミッション確認
chmod 600 .env
```

### Supabase接続エラー
- .envのSUPABASE_URLとSUPABASE_KEYを確認
- Supabaseダッシュボードで認証情報を再確認

## 次回以降の作業予定

1. ✅ プロンプト更新（完了）
2. ✅ DBマイグレーション準備（完了）
3. 🔄 活動登録とX投稿（自宅で実施）
4. ⏳ Qiita/Zenn投稿機能の実装
5. ⏳ 投稿スケジューリング機能
6. ⏳ 投稿履歴管理

## 質問・不明点

- GitHub Issues: https://github.com/toshi776/sns-auto-post/issues
- このプロジェクトのREADME.mdも参照
