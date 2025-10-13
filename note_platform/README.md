# Note Platform モジュール

Gemini APIを使った記事生成とSeleniumを使ったNote.com投稿を管理するモジュール

## 機能

1. **記事生成** (`generate_note.py`)
   - Gemini APIで詳細な技術記事を自動生成
   - タイトルと本文を分離して生成
   - 3つのスタイル対応（技術記事、カジュアル、チュートリアル）
   - 2000-4000文字の充実した記事

2. **Note投稿** (`post_note.py`)
   - Seleniumでブラウザを自動操作
   - Note.comへの自動ログインと記事投稿
   - Dry runモードでテスト可能
   - スクリーンショット保存機能

## 重要な注意事項

**⚠️ Windows環境が必要**

`post_note.py`（Note投稿機能）は、Seleniumによるブラウザ自動操作を使用するため、**Windows環境でGUIブラウザが必要**です。

- ✅ Windows 10/11で動作
- ❌ WSL環境では動作しません（ブラウザGUIが必要なため）
- ✅ `generate_note.py`（記事生成）はWSL環境でも動作します

## セットアップ

### 1. 環境変数設定

`.env`ファイルに以下を追加：

```bash
# Gemini API（既存）
GEMINI_API_KEY=your_gemini_api_key

# Note.com設定
NOTE_EMAIL=your_note_email@example.com
NOTE_PASSWORD=your_note_password

# システム設定
BROWSER_HEADLESS=false  # ヘッドレスモードで実行する場合はtrue
```

### 2. Chrome のインストール（Windows環境）

Seleniumを使用するため、Google Chromeのインストールが必要です：

1. https://www.google.com/chrome/ からChromeをダウンロード
2. インストーラーを実行してインストール
3. ChromeDriverは `webdriver-manager` が自動でセットアップします

### 3. 依存ライブラリ（確認）

```bash
pip install selenium webdriver-manager google-generativeai
```

## 使い方

### 記事生成（WSL環境でも動作）

```bash
# 基本的な使い方（技術記事スタイル）
python note_platform/generate_note.py "今日はPythonでAPIを実装しました"

# カジュアルスタイル
python note_platform/generate_note.py "新しいプロジェクト開始" --style casual

# チュートリアルスタイル
python note_platform/generate_note.py "初心者向けPython入門" --style tutorial
```

**出力例：**
```
================================================================================
✅ Note記事が生成されました
================================================================================

【タイトル】
Gemini API 2.0 FlashとTwitter API v2でX自動投稿システムを構築してみた

================================================================================
【本文】
================================================================================
## はじめに

本記事では、Gemini API 2.0 FlashとTwitter API v2を統合し...

（省略）

================================================================================
📊 タイトル文字数: 52
📊 本文文字数: 4602
```

### Note投稿（Windows環境のみ）

```bash
# Dry runモード（実際には投稿しない）
python note_platform/post_note.py "記事タイトル" "記事本文" --dry-run

# 実際に投稿（ブラウザが開きます）
python note_platform/post_note.py "技術記事のタイトル" "本文..."

# ヘッドレスモード（ブラウザを表示しない）
python note_platform/post_note.py "記事タイトル" "本文..." --headless
```

**⚠️ 注意:**
- 初回実行時は、ChromeDriverの自動ダウンロードが行われます
- ブラウザが自動で開き、Note.comへのログインと投稿が行われます
- 投稿処理中はブラウザを操作しないでください

## 統合ワークフロー例

Activity DBと組み合わせて使う：

```bash
# 1. 活動を記録（WSL環境）
python activity_db/add_activity.py "Phase 3のNote投稿機能を実装完了"

# 2. 最新活動を取得して記事生成（WSL環境）
python note_platform/generate_note.py "Phase 3のNote投稿機能を実装完了" > article.txt

# 3. 生成された記事をNoteに投稿（Windows環境が必要）
# Windows環境に移動してから実行
python note_platform/post_note.py "タイトル" "$(cat article.txt)"
```

## モジュールとして使用

Pythonコードから直接呼び出す：

```python
from note_platform import generate_note_article, post_to_note

# 記事生成
activity = "今日はPythonで新機能を実装しました"
article = generate_note_article(activity, style="technical")

print(f"タイトル: {article['title']}")
print(f"本文: {article['content']}")

# Note投稿（Dry runモード）- Windows環境のみ
result = post_to_note(
    title=article['title'],
    content=article['content'],
    dry_run=True
)
print(result)

# 実際に投稿（Windows環境のみ）
result = post_to_note(
    title=article['title'],
    content=article['content'],
    headless=False,
    dry_run=False
)
print(f"投稿URL: {result['url']}")
```

## 記事スタイルの選択

### 1. technical（技術記事）
- エンジニア・開発者向け
- 実装の詳細、コード例を含む
- 丁寧な「〜です・ます」調

### 2. casual（カジュアル）
- 幅広い読者向け
- 難しい用語を噛み砕いて説明
- 親しみやすい文体

### 3. tutorial（チュートリアル）
- 初心者向け
- ステップバイステップ解説
- 「〜しましょう」という呼びかけ口調

## エラーハンドリング

### よくあるエラー

**1. `GEMINI_API_KEYを.envに設定してください`**
- `.env`ファイルにGEMINI_API_KEYを追加してください

**2. `NOTE_EMAILとNOTE_PASSWORDを.envに設定してください`**
- `.env`ファイルにNote.comのログイン情報を追加してください

**3. `ChromeDriverのセットアップエラー`（Windows環境）**
- Google Chromeがインストールされているか確認
- インターネット接続を確認（ChromeDriverの自動ダウンロードに必要）

**4. `WSL環境での実行エラー`**
- `post_note.py`はWindows環境でのみ動作します
- WSL環境では`generate_note.py`のみ使用可能です

## スクリーンショット機能

Note投稿時、以下の場所にスクリーンショットが保存されます：

- **成功時**: `~/note_post_preview.png`
- **エラー時**: `~/note_post_error.png`

デバッグやトラブルシューティングに活用してください。

## ファイル構成

```
note_platform/
├── __init__.py         # モジュール初期化
├── generate_note.py    # Gemini APIで記事生成
├── post_note.py        # Seleniumで Note投稿（Windows環境のみ）
└── README.md           # 本ファイル
```

## Windows環境での実行手順

### 1. プロジェクトをWindows環境にコピー

WSLからWindows環境にプロジェクトをコピー：

```bash
# WSL環境から
cp -r /home/toshi776/projects/sns-auto-post /mnt/c/Users/[YourUsername]/Projects/
```

### 2. Windows PowerShellで実行

```powershell
# Windowsのプロジェクトディレクトリに移動
cd C:\Users\[YourUsername]\Projects\sns-auto-post

# 仮想環境を作成（初回のみ）
python -m venv venv

# 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# 依存ライブラリをインストール（初回のみ）
pip install -r requirements.txt

# Note投稿を実行
python note_platform\post_note.py "タイトル" "本文" --dry-run
```

## トラブルシューティング

### Selenium関連のエラー

1. **Chromeが起動しない**
   - Chromeが最新バージョンか確認
   - `webdriver-manager`を再インストール: `pip install --upgrade webdriver-manager`

2. **要素が見つからないエラー**
   - Note.comのUI変更の可能性
   - スクリーンショットを確認してページ構造を調査

3. **ログインに失敗**
   - `.env`のメールアドレスとパスワードを確認
   - Note.comで二段階認証を無効化（推奨）

## 次のステップ

Phase 4では、全モジュールを統合したスケジューラーを実装予定：
- 定期的な活動記録
- 自動記事生成
- 自動投稿（X・Note）

## 参考ドキュメント

- [SPECIFICATION.md](../SPECIFICATION.md) - 全体仕様
- [x_platform/README.md](../x_platform/README.md) - X Platform使い方
- [activity_db/README.md](../activity_db/README.md) - Activity DB使い方

---

**重要**: `post_note.py`を実行する際は、必ずWindows環境で実行してください。WSL環境では正常に動作しません。
