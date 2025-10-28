# SNS自動投稿システム

生成AIで作成した文章を各種SNSに自動投稿するシステム

## 概要

このシステムは、生成AI（ChatGPT、Claude、Geminiなど）で作成した投稿文をテキストファイルから読み込み、複数のSNSプラットフォームに自動投稿します。

**ワークフロー：**
```
開発・調査内容
    ↓
生成AIで各チャネル用の文章を生成
    ↓
テキストファイルに保存
    ↓
自動投稿システムで配信（X、Note、その他）
```

## 特徴

- **テキストファイルベース**: 生成AIで作成した投稿文をテキストファイルから読み込み
- **独立したサブシステム**: 各プラットフォームは完全に独立。個別に実行・メンテナンス可能
- **柔軟な文章生成**: ChatGPT、Claude、Geminiなど、任意の生成AIで文章を作成可能
- **一括投稿**: main.pyで複数プラットフォームに一括投稿
- **Dry runモード**: 実際に投稿せずにテスト実行

## システム構成

```
sns-auto-post/
├── x_platform/          # X (Twitter) 投稿システム
│   ├── post_x.py       # 投稿スクリプト
│   ├── requirements.txt
│   └── README.md
│
├── note_platform/       # Note.com 投稿システム
│   ├── post_note.py    # 投稿スクリプト（Windows環境のみ）
│   ├── requirements.txt
│   └── README.md
│
├── main.py             # 一括実行スクリプト
├── requirements.txt    # 全体の依存ライブラリ
├── .env               # 環境変数（API キーなど）
└── README.md          # 本ファイル
```

各サブシステムは**完全に独立**しており、他のシステムに依存しません。

## クイックスタート

### 1. セットアップ

```bash
# プロジェクトに移動
cd /home/toshi776/projects/sns-auto-post

# 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存ライブラリインストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集してAPIキーを設定
```

### 2. 環境変数の設定

`.env` ファイルに以下を設定：

```bash
# X (Twitter) API
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret

# Note.com
NOTE_EMAIL=your_note_email@example.com
NOTE_PASSWORD=your_note_password
```

### 3. 使い方

#### 投稿文の準備

生成AI（ChatGPT、Claude、Geminiなど）で投稿文を作成し、**1つのテキストファイル**に保存：

```bash
# ディレクトリ作成（初回のみ）
mkdir -p posts

# 投稿ファイル作成（UTF-8エンコーディング）
cat > posts/post.txt << 'EOF'
[X]
今日はPythonでテキストファイル読み込み機能を実装しました！🚀

[Note Title]
Pythonでファイル読み込み機能を実装

[Note Content]
今日はPythonでテキストファイル読み込み機能を実装しました。

## 実装内容
- セクション形式のファイルパーサー
- 統合投稿ファイルのサポート
- UTF-8エンコーディング対応

この機能により、生成AIで作成した投稿文を1つのファイルで管理できるようになりました。
EOF
```

**投稿ファイル形式:**
- `[X]`: X (Twitter) 投稿のテキスト
- `[Note Title]`: Note記事のタイトル
- `[Note Content]`: Note記事の本文（複数行OK）
- 不要なセクションは省略可能（例：Xのみ投稿したい場合は`[X]`のみ）

#### 一括投稿（推奨）

統合投稿ファイルで複数プラットフォームに一括投稿：

```bash
# 両方に投稿
python main.py --post-file "posts/post.txt"

# Xのみに投稿（ファイル内に[X]セクションのみ記載）
python main.py --post-file "posts/post.txt"

# Dry runモード（投稿内容の確認）
python main.py --post-file "posts/post.txt" --dry-run

# 個別ファイル指定も可能（従来の方法）
python main.py --x-text-file "posts/x_post.txt"

# 直接テキストを指定
python main.py --x-text "今日の開発成果 🚀"
```

#### 個別に投稿

各サブシステムを個別に実行：

```bash
# X投稿のみ
python x_platform/post_x.py "今日はPythonでAPIを実装しました 🚀"

# Note投稿のみ（Windows環境）
python note_platform/post_note.py "記事タイトル" "本文..."
```

## ワークフロー例

### 生成AIで文章を作成して投稿

```bash
# 1. 生成AI（ChatGPT、Claude、Geminiなど）で投稿文を作成
# プロンプト例: 「以下の形式でSNS投稿文を作成してください」
#
# [X]
# <280文字以内のX投稿文>
#
# [Note Title]
# <記事タイトル>
#
# [Note Content]
# <2000-4000文字の技術記事>

# 2. 生成された文章をコピー＆ペーストして保存（UTF-8エンコーディング）
# テキストエディタで posts/post.txt に保存
# または以下のようにファイル作成:

cat > posts/post.txt << 'EOF'
[X]
今日はPythonでREST APIを実装しました 🚀
FastAPIを使って高速なAPIサーバーを構築しました。

[Note Title]
PythonでREST API開発：FastAPI実践ガイド

[Note Content]
今日はPythonでREST APIを実装しました。
FastAPIを使って高速なAPIサーバーを構築する方法を紹介します。

## 実装内容
- エンドポイント設計
- データバリデーション
- 自動ドキュメント生成

詳細は記事をご覧ください。
EOF

# 3. 投稿前に内容を確認（Dry run）
python main.py --post-file "posts/post.txt" --dry-run

# 4. 問題なければ本番投稿
python main.py --post-file "posts/post.txt"
```

## サブシステムの詳細

### X投稿システム

- **ディレクトリ**: `x_platform/`
- **対応環境**: WSL/Linux/Windows
- **詳細**: [x_platform/README.md](./x_platform/README.md)

**使い方：**
```bash
cd x_platform
python post_x.py "投稿する文章" [--dry-run]
```

### Note投稿システム

- **ディレクトリ**: `note_platform/`
- **対応環境**: Windows のみ（Selenium使用）
- **詳細**: [note_platform/README.md](./note_platform/README.md)

**使い方（Windows環境）：**
```bash
cd note_platform
python post_note.py "タイトル" "本文" [--dry-run] [--headless]
```

## 必要な環境

### 共通
- Python 3.12+
- X (Twitter) API キー
- Note.com アカウント

### プラットフォーム別
- **X投稿**: どのOS でも動作
- **Note投稿**: Windows環境のみ（Google Chrome必須）

## 開発環境の使い分け

- **WSL/Linux**: X投稿システムの開発・実行
- **Windows**: Note投稿システムの実行（Selenium使用のため）

## トラブルシューティング

### X投稿の問題

`.env`の設定を確認：
```bash
# X APIの認証情報が4つすべて設定されているか確認
grep "^X_" .env
```

詳細は [x_platform/README.md](./x_platform/README.md) を参照。

### Note投稿の問題

- **Windows環境で実行していますか？** WSLでは動作しません
- **Google Chromeがインストールされていますか？**
- **`.env`のNote.comログイン情報は正しいですか？**

詳細は [note_platform/README.md](./note_platform/README.md) を参照。

## 今後の拡張

新しいプラットフォームを追加する場合：

1. `{platform}_platform/` ディレクトリを作成
2. `post_{platform}.py` を実装
3. `requirements.txt` を追加
4. `README.md` でドキュメント化
5. `main.py` に統合（オプション）

各サブシステムが独立しているため、容易に拡張できます。

## ライセンス

Private Project

## 関連ドキュメント

- [X投稿システム](./x_platform/README.md)
- [Note投稿システム](./note_platform/README.md)
