# SNS自動投稿システム

日々の開発や活動を自動的に各種SNSに投稿するシステム

## 🎯 概要

活動内容を入力すると、自動的にX（Twitter）やNote.comなどの各種SNSプラットフォームに最適化された投稿を生成・配信します。

## 📋 ドキュメント

- **[SPECIFICATION.md](./SPECIFICATION.md)**: 詳細な仕様書

## 🏗️ システム構成

```
活動内容入力 → Supabase DB → X投稿 → Note投稿 → その他SNS
```

### モジュール構成

- **activity_db/**: 活動情報データベース管理
- **x_platform/**: X（Twitter）投稿
- **note_platform/**: Note.com投稿
- **main.py**: 統合実行スクリプト

各モジュールは完全に独立しており、個別に動作・削除可能です。

## 🚀 クイックスタート

### 1. セットアップ

```bash
# リポジトリクローン
cd /path/to/projects
git clone <repository-url> sns-auto-post
cd sns-auto-post

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存ライブラリインストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集してAPIキーを設定
```

### 2. 活動を記録

```bash
cd activity_db
python add_activity.py "今日の開発内容"
```

### 3. SNSに投稿

```bash
# X投稿のみ
cd ../x_platform
python post_x.py --latest

# Note投稿のみ
cd ../note_platform
python post_note.py --latest

# すべて一括投稿
cd ..
python main.py --latest
```

## 📦 必要な環境

- Python 3.12+
- Supabase アカウント
- Gemini API キー
- X (Twitter) API キー
- Note.com アカウント

## 🔧 開発環境

- **WSL**: activity_db, x_platform 開発
- **Windows**: note_platform (Selenium) 開発

## 📄 ライセンス

Private Project

## 📞 問い合わせ

詳細は [SPECIFICATION.md](./SPECIFICATION.md) を参照してください。
