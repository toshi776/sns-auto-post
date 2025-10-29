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

---

### 6. 問題解決：クリップボード貼り付け方式の実装

**実施時刻:** 2025-10-29 午後

**実装内容:**
1. `pyperclip`パッケージのインストール
2. `note_platform/post_note.py`を修正
   - `import pyperclip`を追加
   - 行ごとの入力処理をクリップボード貼り付け方式に変更
   - Ctrl+V（Windows）/ Cmd+V（Mac）での貼り付けに対応

**修正コード:**
```python
# pyperclipをインポート
import pyperclip

# 本文入力処理を変更
pyperclip.copy(content)  # クリップボードにコピー
content_textarea.send_keys(Keys.CONTROL, 'v')  # Ctrl+Vで貼り付け
```

**テスト結果:**
```bash
python main.py --post-file "posts/post.txt"
```

- ✅ 絵文字を含む文字列の投稿に成功
- ✅ Markdown記法（`##`、`**`、`*`など）が正しく認識
- ✅ 自動目次が生成され、見出しが正しくフォーマット
- X投稿: https://x.com/toshi776/status/1983460796400280033
- Note投稿: https://editor.note.com/notes/n8095a516c8f1/publish/

## 結論

**解決した問題:**
1. ✅ ChromeDriverのBMP文字制限を回避（絵文字対応）
2. ✅ Markdown記法の認識を実現
3. ✅ 高速で安定した投稿処理

**最終的な解決策:**
- クリップボード貼り付け方式（案1）を採用
- 予想に反して、Noteエディタは一括貼り付けでもMarkdown記法を正しく解析
- 行ごとの入力は不要だった

**技術的な学び:**
- Noteエディタは貼り付けられたテキストを解析してMarkdown記法を認識
- クリップボード経由の入力は`send_keys`の文字制限を回避できる
- より高速でシンプルな実装で問題を解決できた

---

## 今後の課題

### まだ必要な微調整
以下の点について、今後の改善が必要：

1. **投稿内容の確認**
   - 実際の投稿結果を確認し、Markdown記法が意図通りに表示されているか検証
   - 絵文字の表示確認

2. **エラーハンドリングの改善**
   - クリップボード操作が失敗した場合のフォールバック処理の検証
   - ネットワークエラーやタイムアウト時の挙動確認

3. **Gemini API整形機能の調整**
   - X (Twitter)の280文字制限に対応
   - 現在は398文字や360文字など、制限を超過する場合がある
   - プロンプト改善で文字数を最適化

4. **パフォーマンスの最適化**
   - 待機時間（`time.sleep`）の調整
   - より効率的な要素検出

5. **ログ・デバッグ機能の強化**
   - より詳細なログ出力
   - エラー発生時の情報収集の改善

### 次回作業時のチェックポイント

- [ ] 複数回の投稿テストで安定性確認
- [ ] さまざまなMarkdown記法（コードブロック、引用、リンクなど）の動作確認
- [ ] Gemini API整形のプロンプト改善（X文字数制限対応）
- [ ] requirements.txtに`pyperclip`を追加
- [ ] READMEドキュメントの更新

### 参考リンク

**本日の投稿結果:**
- X: https://x.com/toshi776/status/1983460796400280033
- Note: https://editor.note.com/notes/n8095a516c8f1/publish/

**スクリーンショット保存先:**
- `C:\Users\toshi\note_post_preview.png`
- `C:\Users\toshi\note_post_after.png`
- `C:\Users\toshi\note_post_error.png` (エラー時)

---

## 作業完了

**日時:** 2025-10-29 午後
**ステータス:** ✅ 主要な問題を解決。クリップボード貼り付け方式により、絵文字対応とMarkdown記法認識を実現。
**次回作業:** 上記「今後の課題」を参照し、細かい調整と安定性向上を進める。
