# X Platform モジュール

Gemini APIを使った投稿文生成とTwitter APIを使ったX投稿を管理するモジュール

## 機能

1. **投稿文生成** (`generate_x.py`)
   - Gemini APIで魅力的なX投稿文を自動生成
   - 活動内容から280文字以内の投稿文を作成
   - ハッシュタグと絵文字を自動挿入

2. **X投稿** (`post_x.py`)
   - Twitter API v2でXに投稿
   - Dry runモードでテスト可能
   - 投稿URLの自動取得

## セットアップ

### 1. 環境変数設定

`.env`ファイルに以下を追加：

```bash
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# X API（Twitter）
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 2. APIキーの取得

#### Gemini API
1. https://makersuite.google.com/app/apikey にアクセス
2. 「Get API Key」をクリック
3. APIキーをコピーして`.env`に追加

#### X (Twitter) API
1. https://developer.x.com/ にアクセス
2. プロジェクトとアプリを作成
3. API Key & Secret, Access Token & Secret を取得
4. `.env`に追加

## 使い方

### 投稿文生成

```bash
# 基本的な使い方
python x_platform/generate_x.py "今日はPythonでAPIを実装しました"

# 文字数制限を指定
python x_platform/generate_x.py "新しいプロジェクト開始" --max-length 140
```

**出力例：**
```
============================================================
✅ X投稿文が生成されました
============================================================
今日はPython×API実装で進捗バリバリ💻✨

コード書くの楽しすぎる🚀
明日も頑張るぞー！

#Python #API開発
============================================================
📊 文字数: 67/280
```

### X投稿

```bash
# Dry runモード（実際には投稿しない）
python x_platform/post_x.py "テスト投稿" --dry-run

# 実際に投稿
python x_platform/post_x.py "Hello, X!"
```

**出力例（実投稿）：**
```
============================================================
✅ Xに投稿しました
============================================================
🆔 Tweet ID: 1234567890
🔗 URL: https://x.com/username/status/1234567890
📊 文字数: 9
```

## 統合ワークフロー例

Activity DBと組み合わせて使う：

```bash
# 1. 活動を記録
python activity_db/add_activity.py "Phase 2のX投稿機能を実装完了"

# 2. 最新活動を取得して投稿文生成
ACTIVITY=$(python activity_db/list_activities.py --latest | grep "内容:" | cut -d: -f2-)
python x_platform/generate_x.py "$ACTIVITY" > post.txt

# 3. 生成された文章を投稿
python x_platform/post_x.py "$(cat post.txt)"
```

## モジュールとして使用

Pythonコードから直接呼び出す：

```python
from x_platform import generate_x_post, post_to_x

# 投稿文生成
activity = "今日はPythonで新機能を実装しました"
post_text = generate_x_post(activity, max_length=280)

# X投稿（Dry runモード）
result = post_to_x(post_text, dry_run=True)
print(result)

# 実際に投稿
result = post_to_x(post_text, dry_run=False)
print(f"投稿URL: {result['url']}")
```

## エラーハンドリング

### よくあるエラー

**1. `GEMINI_API_KEYを.envに設定してください`**
- `.env`ファイルにGEMINI_API_KEYを追加してください

**2. `X API認証情報を.envに設定してください`**
- `.env`ファイルにX APIの4つの認証情報を追加してください

**3. `TweepyException: 403 Forbidden`**
- X APIの権限設定を確認してください
- アプリに「Read and Write」権限が必要です

**4. `生成された文章が280文字を超えています`**
- 自動的に切り詰められますが、`--max-length`で調整可能です

## API使用制限

### Gemini API
- 無料枠: 15 RPM (Requests Per Minute)
- 月間制限: 60 RPM

### X API (Free tier)
- 月間投稿数: 1,500ツイート
- レート制限: 17投稿/15分

## ファイル構成

```
x_platform/
├── __init__.py         # モジュール初期化
├── generate_x.py       # Gemini APIで投稿文生成
├── post_x.py           # Twitter APIでX投稿
└── README.md           # 本ファイル
```

## 次のステップ

Phase 3では、Note投稿機能を実装予定：
- `note_platform/` モジュール
- Selenium自動操作でNote投稿
- Gemini APIで記事本文生成

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. `.env`ファイルが正しく設定されているか
2. APIキーが有効か
3. インターネット接続が正常か
4. API使用制限に達していないか

詳細は [SPECIFICATION.md](../SPECIFICATION.md) を参照してください。
