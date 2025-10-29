# 作業記録 2025-10-29

## 実施した作業

### 1. 自動投稿システムの初回実行
- 依存パッケージのインストール
- `.env`ファイルに認証情報を設定
- `posts/post.txt`を使用してX (Twitter)とNote.comに投稿成功

**投稿結果:**
- X: https://x.com/toshi776/status/1983321858180304900
- Note: https://editor.note.com/notes/n48817545bba9/publish/

### 2. 問題発見：NoteでMarkdown記法が正しく表示されない

**問題内容:**
- `post.txt`の`[Note Content]`セクションにMarkdown記法（`##`、`**`、`` ` ``など）を使用
- Noteエディタに投稿すると、記法がそのまま文字として表示される
- 見出しや太字などのフォーマットが適用されない

**原因調査:**
- Noteエディタは独自のMarkdown風記法をサポート（`##` + スペースで大見出しなど）
- スクリプトが`send_keys(content)`で全文を一気に入力しているため、記法が認識されない
- Noteは行ごとにEnterキーを押した時に記法を解釈する仕様

### 3. Gemini API整形機能のテスト

**実行コマンド:**
```bash
python main.py --post-file "posts/post.txt" --use-gemini
```

**結果:**
- Gemini APIが文章を整形（Markdown記号を適切に処理）
- しかし、投稿時は同じ問題が発生（記法がそのまま表示）
- X投稿: https://x.com/toshi776/status/1983326700839768121
- Note投稿: https://editor.note.com/notes/n79066e89a7b4/publish/

**Gemini整形の効果:**
- X投稿: 398文字 → 360文字（ただし280文字制限超過）
- Note本文: 1,659文字 → 1,770文字

### 4. スクリプト修正：行ごとの入力を実装

**修正内容:**
- `note_platform/post_note.py`を修正
- `Keys`のインポートを追加
- 本文を行ごとに分割して入力し、各行の後にEnterキーを送信
- 進捗表示とフォールバック処理を追加

**コード変更:**
```python
# 修正前
content_textarea.send_keys(content)

# 修正後
lines = content.split('\n')
for i, line in enumerate(lines):
    if i > 0:
        content_textarea.send_keys(Keys.RETURN)
        time.sleep(0.05)
    content_textarea.send_keys(line)
```

### 5. 修正版スクリプトのテスト

**実行結果:**
```
⚠️  行ごとの入力に失敗: Message: unknown error: ChromeDriver only supports characters in the BMP
```

**問題:**
- ChromeDriverが絵文字（👍、🚀など）を含む文字列を`send_keys`で送信できない
- フォールバック処理により一括入力で投稿された
- 結果、Markdown記法は認識されず

**投稿結果:**
- X投稿: https://x.com/toshi776/status/1983327768269242637
- Note投稿: https://editor.note.com/notes/n5046bd409e35/publish/

## 現在の課題

### 主な問題
1. **ChromeDriverの文字制限**: BMP（Basic Multilingual Plane）外の文字（絵文字など）を`send_keys`で送信できない
2. **Markdown記法の認識**: 一括入力ではNoteが記法を認識しない

### 解決策の候補

#### 案1: クリップボード貼り付け方式
- `pyperclip`を使用してクリップボード経由で貼り付け
- 絵文字も含めて全文字対応
- より高速

#### 案2: Gemini APIプロンプト改善
- Noteが一括入力でも認識できる形式に整形
- Markdown記法を使わず、プレーンテキストに近い形式
- 見出しは装飾記号や改行で表現

#### 案3: JavaScript経由で入力
- `driver.execute_script`を使用してJavaScript経由で入力
- DOM操作により直接テキストを挿入
- ただし、Noteの記法認識には効果がない可能性

## 技術情報

### 使用技術
- Python 3.12
- Selenium 4.38.0
- ChromeDriver（webdriver-manager経由）
- Gemini API（google-generativeai 0.8.5）
- Tweepy 4.16.0（X投稿）

### 環境
- OS: Windows
- ブラウザ: Google Chrome 141.0.7390.123

### プロジェクト構成
```
sns-auto-post/
├── main.py                 # 統合投稿スクリプト
├── gemini_formatter.py     # Gemini API整形モジュール
├── x_platform/
│   └── post_x.py          # X投稿モジュール
├── note_platform/
│   └── post_note.py       # Note投稿モジュール（今回修正）
└── posts/
    └── post.txt           # 投稿ファイル
```

## 次のステップ

1. クリップボード貼り付け方式の実装を検討
2. または、Gemini APIプロンプトを改善してNote用の最適な形式を生成
3. 実装後、テスト投稿で動作確認

## 参考情報

- NoteエディタはMarkdown風記法をサポート（`##`、`###`など）
- 記法の認識にはEnterキーでの改行が必要
- ChromeDriverの`send_keys`はBMP外の文字（絵文字など）に対応していない
- X (Twitter)の文字数制限は280文字

## メモ

- Gemini APIは毎回異なる整形結果を生成する（文字数が変動）
- Note投稿時のスクリーンショット保存機能が有効
  - 投稿前: `C:\Users\toshi\note_post_preview.png`
  - 投稿後: `C:\Users\toshi\note_post_after.png`
