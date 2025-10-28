# Note投稿システム

Note.com に記事を投稿するための独立したサブシステム

## 概要

外部から渡されたタイトルと本文をNote.comに投稿します。完全に独立したモジュールで、他のシステムに依存しません。

## 重要な注意事項

**⚠️ Windows環境が必要**

このシステムは、Seleniumによるブラウザ自動操作を使用するため、**Windows環境でGUIブラウザが必要**です。

- ✅ Windows 10/11で動作
- ❌ WSL環境では動作しません（ブラウザGUIが必要なため）

## 機能

- Seleniumでブラウザを自動操作してNote.comに投稿
- 自動ログインと記事投稿
- Dry runモードでテスト可能
- スクリーンショット保存機能（デバッグ用）

## セットアップ

### 1. Chrome のインストール（Windows環境）

Google Chromeのインストールが必要です：

1. https://www.google.com/chrome/ からChromeをダウンロード
2. インストーラーを実行してインストール
3. ChromeDriverは `webdriver-manager` が自動でセットアップします

### 2. 依存ライブラリのインストール

```bash
cd note_platform
pip install -r requirements.txt
```

### 3. 環境変数の設定

プロジェクトルートの `.env` ファイルに以下を設定：

```bash
NOTE_EMAIL=your_note_email@example.com
NOTE_PASSWORD=your_note_password

# オプション: ヘッドレスモードで実行する場合
BROWSER_HEADLESS=false
```

## 使い方

### コマンドラインから実行

```bash
# Dry runモード（実際には投稿しない）
python post_note.py "記事タイトル" "記事本文" --dry-run

# 実際に投稿（ブラウザが開きます）
python post_note.py "技術記事のタイトル" "本文はここに書きます..."

# ヘッドレスモード（ブラウザを表示しない）
python post_note.py "記事タイトル" "本文..." --headless
```

**実行例：**
```bash
$ python post_note.py "PythonでAPI開発" "今日はPythonでREST APIを実装しました..."
📤 Note.comに投稿準備中...
📝 タイトル: PythonでAPI開発
📊 本文文字数: 35

🔧 ChromeDriverをセットアップ中...
✅ ChromeDriverのセットアップ完了
🌐 Note.comにアクセス中...
🔑 ログイン中...
✅ ログイン完了
📝 記事作成ページに移動中...
✍️  タイトルを入力中...
✍️  本文を入力中...
🚀 記事を公開中...
✅ 記事を公開しました！

============================================================
✅ Note.comに投稿しました
============================================================
📝 タイトル: PythonでAPI開発
🔗 URL: https://note.com/username/n/xxxxx
📊 本文文字数: 35
```

**⚠️ 注意:**
- 初回実行時は、ChromeDriverの自動ダウンロードが行われます
- ブラウザが自動で開き、Note.comへのログインと投稿が行われます
- 投稿処理中はブラウザを操作しないでください

### Pythonコードから呼び出し

```python
from note_platform.post_note import post_to_note

# 投稿
result = post_to_note(
    title="記事タイトル",
    content="記事本文...",
    headless=False,
    dry_run=False
)
print(f"投稿URL: {result['url']}")

# Dry run
result = post_to_note(
    title="テスト記事",
    content="テスト本文",
    dry_run=True
)
```

## レスポンス形式

```python
{
    'success': True,              # 成功/失敗
    'url': 'https://...',        # 記事URL (成功時のみ)
    'title': '記事タイトル',
    'content_length': 1234,      # 本文文字数
    'dry_run': False             # Dry runモードかどうか
}
```

## スクリーンショット機能

Note投稿時、以下の場所にスクリーンショットが保存されます：

- **投稿前**: `~/note_post_preview.png`
- **投稿後**: `~/note_post_after.png`
- **エラー時**: `~/note_post_error.png`

デバッグやトラブルシューティングに活用してください。

## エラーハンドリング

### よくあるエラー

**1. `NOTE_EMAILとNOTE_PASSWORDを.envに設定してください`**
- `.env`ファイルにNote.comのログイン情報を追加してください

**2. `ChromeDriverのセットアップエラー`**
- Google Chromeがインストールされているか確認
- インターネット接続を確認（ChromeDriverの自動ダウンロードに必要）

**3. `要素が見つからないエラー`**
- Note.comのUI変更の可能性
- スクリーンショットを確認してページ構造を調査

**4. `ログインに失敗`**
- `.env`のメールアドレスとパスワードを確認
- Note.comで二段階認証を無効化（推奨）

**5. `WSL環境での実行エラー`**
- このシステムはWindows環境でのみ動作します

## Windows環境での実行手順

### WSLからWindows環境にプロジェクトをコピー

```bash
# WSL環境から
cp -r /home/toshi776/projects/sns-auto-post /mnt/c/Users/[YourUsername]/Projects/
```

### Windows PowerShellで実行

```powershell
# Windowsのプロジェクトディレクトリに移動
cd C:\Users\[YourUsername]\Projects\sns-auto-post

# 仮想環境を作成（初回のみ）
python -m venv venv

# 仮想環境を有効化
.\venv\Scripts\Activate.ps1

# 依存ライブラリをインストール（初回のみ）
pip install -r note_platform\requirements.txt

# Note投稿を実行
python note_platform\post_note.py "タイトル" "本文" --dry-run
```

## ファイル構成

```
note_platform/
├── __init__.py         # モジュール初期化
├── post_note.py        # Note投稿機能（Windows環境のみ）
├── requirements.txt    # 依存ライブラリ
└── README.md           # 本ファイル
```

## ワークフロー例

ChatGPTで生成した記事を投稿：

```bash
# 1. ChatGPTで記事を生成（手動またはAPI経由）
# タイトルと本文をファイルに保存
echo "PythonでAPI開発" > title.txt
echo "今日はPythonでREST APIを実装しました..." > content.txt

# 2. Note投稿システムで投稿（Windows環境）
python note_platform\post_note.py "$(cat title.txt)" "$(cat content.txt)"
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

4. **文字化けが発生**
   - Windows PowerShellのエンコーディングを確認
   - `chcp 65001` コマンドでUTF-8に設定

## 注意事項

- Seleniumによるブラウザ自動操作を使用します
- Note.comのログイン情報が必要です
- Note.comのUIが変更された場合、動作しなくなる可能性があります
- 二段階認証が有効な場合、自動ログインできません（無効化推奨）

---

**重要**: このシステムは必ずWindows環境で実行してください。WSL環境では正常に動作しません。
