# X投稿システム

X (Twitter) に投稿するための独立したサブシステム

## 概要

外部から渡された文章をX (Twitter) に投稿します。完全に独立したモジュールで、他のシステムに依存しません。

## 機能

- Tweepy (Twitter API v2) を使用してXに投稿
- Dry runモードでテスト実行
- コマンドライン/Python関数の両方で利用可能

## セットアップ

### 1. 依存ライブラリのインストール

```bash
cd x_platform
pip install -r requirements.txt
```

### 2. 環境変数の設定

プロジェクトルートの `.env` ファイルに以下を設定：

```bash
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 3. X API キーの取得方法

1. https://developer.x.com/ にアクセス
2. プロジェクトとアプリを作成
3. API Key & Secret, Access Token & Secret を取得
4. アプリに「Read and Write」権限を付与
5. `.env`に追加

## 使い方

### コマンドラインから実行

```bash
# 通常投稿
python post_x.py "投稿する文章"

# Dry runモード（実際には投稿しない）
python post_x.py "テスト投稿" --dry-run
```

**実行例：**
```bash
$ python post_x.py "Hello, X!"
📤 Xに投稿中...
📝 投稿内容:
------------------------------------------------------------
Hello, X!
------------------------------------------------------------

============================================================
✅ Xに投稿しました
============================================================
🆔 Tweet ID: 1234567890
🔗 URL: https://x.com/username/status/1234567890
📊 文字数: 9
```

### Pythonコードから呼び出し

```python
from x_platform.post_x import post_to_x

# 投稿
result = post_to_x("投稿する文章")
print(f"投稿URL: {result['url']}")

# Dry run
result = post_to_x("テスト投稿", dry_run=True)
```

## レスポンス形式

```python
{
    'success': True,          # 成功/失敗
    'tweet_id': '...',       # ツイートID (成功時のみ)
    'url': 'https://...',    # ツイートURL (成功時のみ)
    'text': '投稿した文章',
    'dry_run': False         # Dry runモードかどうか
}
```

## 注意事項

- Twitter API v2を使用します
- API利用には Twitter Developer アカウントが必要です
- 投稿は最大280文字までです
- API制限: Free tier は月間1,500ツイート、17投稿/15分

## エラーハンドリング

### よくあるエラー

**1. `X API認証情報を.envに設定してください`**
- `.env`ファイルにX APIの4つの認証情報を追加してください

**2. `TweepyException: 403 Forbidden`**
- X APIの権限設定を確認してください
- アプリに「Read and Write」権限が必要です

**3. `TweepyException: 429 Too Many Requests`**
- レート制限に達しています。しばらく待ってから再試行してください

## ファイル構成

```
x_platform/
├── __init__.py         # モジュール初期化
├── post_x.py           # X投稿機能
├── requirements.txt    # 依存ライブラリ
└── README.md           # 本ファイル
```

## ワークフロー例

ChatGPTで生成した文章を投稿：

```bash
# 1. ChatGPTで文章を生成（手動またはAPI経由）
# 文章をファイルに保存
echo "今日はPythonでAPIを実装しました 🚀" > tweet.txt

# 2. X投稿システムで投稿
python x_platform/post_x.py "$(cat tweet.txt)"
```

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. `.env`ファイルが正しく設定されているか
2. APIキーが有効か（X Developer Portalで確認）
3. アプリに「Read and Write」権限があるか
4. インターネット接続が正常か
5. API使用制限に達していないか
