# SNS自動投稿システム - 仕様書

## 📋 システム概要

### ゴール
日々の開発や活動を自動的に各種SNSに投稿する

### 設計方針
- 極限までシンプルに
- 各モジュール完全独立
- 一から新規作成（既存コード流用なし）

---

## 🏗️ アーキテクチャ

```
活動内容入力（CLI/ClaudeCode/CodeX等）
    ↓
活動情報DBに保存（Supabase）
    ↓
X投稿プログラム実行
    ├─ 活動情報DBから取得
    ├─ GeminiAPIでX投稿文生成
    └─ X APIで自動投稿
    ↓
Note投稿プログラム実行
    ├─ 活動情報DBから取得
    ├─ GeminiAPIでNote記事生成
    └─ Seleniumでブラウザ自動投稿
    ↓
（将来）その他SNS投稿機能追加
```

---

## 🗄️ データベース設計

### 使用DB
**Supabase（PostgreSQL）**
- 無料枠: 500MB
- 複数環境からアクセス可能
- REST API提供

### テーブル構造

#### activities テーブル
```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_activities_timestamp ON activities(timestamp DESC);
```

### データ構造（JSON表現）
```json
{
    "id": "uuid-string",
    "timestamp": "2025-01-12T10:30:00+09:00",
    "content": "活動内容の本文",
    "created_at": "2025-01-12T10:30:00+09:00"
}
```

### 容量管理
- **古いデータ削除**: 90日以上前のデータを自動削除
- **VACUUM実行**: DELETE後に容量を実際に解放
- 参考: https://zenn.dev/shimotani/articles/45206b9aacdad7

---

## 📁 ディレクトリ構成

```
sns-auto-post/
├── activity_db/              # 活動情報DB関連（独立モジュール）
│   ├── __init__.py
│   ├── db.py                 # DB操作コア
│   ├── add_activity.py       # 活動追加CLI
│   ├── list_activities.py    # 活動一覧表示CLI
│   ├── cleanup.py            # 古いデータ削除+VACUUM
│   └── README.md             # 使い方
│
├── x_platform/               # X投稿関連（独立モジュール）
│   ├── __init__.py
│   ├── post_x.py             # X投稿実行
│   ├── generate_x.py         # X用コンテンツ生成（Gemini）
│   └── README.md             # 使い方
│
├── note_platform/            # Note投稿関連（独立モジュール）
│   ├── __init__.py
│   ├── post_note.py          # Note投稿実行
│   ├── generate_note.py      # Note用コンテンツ生成（Gemini）
│   └── README.md             # 使い方
│
├── main.py                   # 統合実行スクリプト
├── .env.example              # 環境変数テンプレート
├── .gitignore                # Git管理除外設定
├── requirements.txt          # 依存ライブラリ
├── SPECIFICATION.md          # 本仕様書
└── README.md                 # プロジェクト概要
```

**特徴**:
- 各フォルダ完全独立 → フォルダごと削除可能
- 各モジュールに独自のREADME
- main.py は各モジュールを順次呼び出すだけ

---

## 🔄 実行フロー

### 1. 活動を記録
```bash
cd activity_db
python add_activity.py "ClaudeCodeでDB設計完了"
# → Supabaseに保存、IDを返す
```

### 2. X投稿のみ実行
```bash
cd x_platform
python post_x.py --latest
# または特定のIDを指定
python post_x.py --activity-id <uuid>
```

### 3. Note投稿のみ実行
```bash
cd note_platform
python post_note.py --latest
```

### 4. すべて一括実行
```bash
python main.py --latest
# → activity_db読み込み → X投稿 → Note投稿
```

### 5. 古いデータ削除
```bash
cd activity_db
python cleanup.py --days 90
# → 90日以上前のデータ削除 + VACUUM実行
```

---

## 🛠️ 開発フェーズ

### Phase 1: 活動情報DB（最優先）
**開発環境**: WSL + ClaudeCode

**実装内容**:
```
activity_db/
├── db.py
│   ├── init_db()              # Supabaseテーブル初期化
│   ├── add_activity(content)  # 活動追加
│   ├── get_activity(id)       # ID指定取得
│   └── get_latest()           # 最新取得
├── cleanup.py
│   └── cleanup_old_data(days) # 古いデータ削除+VACUUM
└── add_activity.py            # CLI
```

**成果物**: 活動を保存・取得・削除できるDB

---

### Phase 2: X投稿
**開発環境**: WSL + ClaudeCode

**実装内容**:
```
x_platform/
├── generate_x.py
│   └── generate_x_content(activity_content) -> str
│       # Gemini APIで280字以内のX投稿文生成
└── post_x.py
    └── post_to_x(activity_id)
        # 1. activity_db から取得
        # 2. generate_x_content() で生成
        # 3. Twitter API で投稿
        # 4. 結果をログ出力
```

**成果物**: 活動内容からX投稿できる

---

### Phase 3: Note投稿
**開発環境**: Windows + ClaudeCode/CodeX

**実装内容**:
```
note_platform/
├── generate_note.py
│   └── generate_note_content(activity_content) -> dict
│       # Gemini APIで記事タイトル・本文生成
└── post_note.py
    └── post_to_note(activity_id)
        # 1. activity_db から取得
        # 2. generate_note_content() で生成
        # 3. Selenium でNote投稿
        # 4. 結果をログ出力
```

**成果物**: 活動内容からNote投稿できる

---

### Phase 4: 統合実行
**開発環境**: WSL + ClaudeCode

**実装内容**:
```python
# main.py
import sys
sys.path.append('./activity_db')
sys.path.append('./x_platform')
sys.path.append('./note_platform')

from activity_db.db import get_latest
from x_platform.post_x import post_to_x
from note_platform.post_note import post_to_note

def main():
    activity = get_latest()

    # X投稿（失敗しても続行）
    try:
        post_to_x(activity['id'])
        print("✅ X投稿成功")
    except Exception as e:
        print(f"❌ X投稿失敗: {e}")

    # Note投稿（失敗しても続行）
    try:
        post_to_note(activity['id'])
        print("✅ Note投稿成功")
    except Exception as e:
        print(f"❌ Note投稿失敗: {e}")
```

**成果物**: 一括自動投稿システム完成

---

## 📦 技術スタック

### 共通
- Python 3.12+
- python-dotenv (環境変数管理)

### activity_db
- supabase-py (Supabase Python SDK)

### x_platform
- google-generativeai (Gemini API)
- tweepy (X/Twitter API v2)

### note_platform
- google-generativeai (Gemini API)
- selenium (ブラウザ自動化)
- webdriver-manager (ChromeDriver自動管理)

### requirements.txt
```txt
# 共通
python-dotenv>=1.0.0

# activity_db
supabase>=2.0.0

# x_platform
google-generativeai>=0.3.2
tweepy>=4.14.0

# note_platform
google-generativeai>=0.3.2
selenium>=4.0.0
webdriver-manager>=4.0.0
```

---

## ⚙️ 環境変数設定

### .env（Git管理外、完全ローカル）
```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# X (Twitter) API
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_TOKEN_SECRET=your_x_access_token_secret
X_BEARER_TOKEN=your_x_bearer_token

# Note.com
NOTE_EMAIL=your_note_email
NOTE_PASSWORD=your_note_password
```

### .env.example（Gitに含める）
```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# X (Twitter) API
X_API_KEY=your_x_api_key_here
X_API_SECRET=your_x_api_secret_here
X_ACCESS_TOKEN=your_x_access_token_here
X_ACCESS_TOKEN_SECRET=your_x_access_token_secret_here
X_BEARER_TOKEN=your_x_bearer_token_here

# Note.com
NOTE_EMAIL=your_note_email_here
NOTE_PASSWORD=your_note_password_here
```

**重要**: `.env` は絶対にGitにコミットしない（.gitignoreに追加）

---

## 🔒 セキュリティ

### Git管理外ファイル（.gitignore）
```
# 環境変数
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# ログ
*.log
logs/
```

---

## 🎯 エラーハンドリング方針

### 各モジュールの独立性
- X投稿が失敗してもNote投稿は実行
- Note投稿が失敗しても他のプラットフォームに影響なし
- エラーは標準出力 + ログファイルに記録

### エラー処理例
```python
def main():
    results = {}

    try:
        x_result = post_to_x(activity_id)
        results['x'] = {'success': True, 'data': x_result}
    except Exception as e:
        results['x'] = {'success': False, 'error': str(e)}
        print(f"❌ X投稿失敗: {e}")

    try:
        note_result = post_to_note(activity_id)
        results['note'] = {'success': True, 'data': note_result}
    except Exception as e:
        results['note'] = {'success': False, 'error': str(e)}
        print(f"❌ Note投稿失敗: {e}")

    return results
```

---

## 📝 開発ルール

### 1. 完全疎結合
- 各プラットフォームフォルダは独立
- 依存関係は activity_db のみ（データ取得のみ）
- 相互参照禁止

### 2. シンプル第一
- 複雑な機能は追加しない
- 必要最小限の実装
- コメント・ドキュメント充実

### 3. コンテンツ生成
- プラットフォームごとに異なるスタイル
- 各開発時に個別相談

### 4. 環境変数
- 重要情報は .env に記載
- ClaudeCode は .env を触らない
- .env.example のみGit管理

---

## 🚀 次のアクション

### Phase 1: activity_db 実装開始
1. ディレクトリ構造作成
2. Supabaseプロジェクト作成・テーブル設定
3. db.py 実装
4. cleanup.py 実装
5. add_activity.py 実装
6. 動作確認

---

## 📅 更新履歴

- 2025-01-12: 初版作成
