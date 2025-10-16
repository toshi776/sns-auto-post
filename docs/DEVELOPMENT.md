# SNS自動投稿システム - 開発履歴

## 📅 開発タイムライン

### 2025-10-13

#### Windows環境でのNote投稿機能の動作確認と改善

**実施内容**

1. **GitHubリポジトリからプロジェクトをプル**
   - `https://github.com/toshi776/sns-auto-post` からクローン完了

2. **依存ライブラリのインストール**
   - `python-dotenv`, `supabase`, `google-generativeai`, `tweepy`, `selenium`, `webdriver-manager` をインストール
   - Windows環境でのエンコーディング問題を解決

3. **Windows環境でのNote自動投稿機能の完全実装**
   - UTF-8エンコーディング対応（絵文字表示の問題を解決）
   - Chrome実行パス（`C:\Program Files\Google\Chrome\Application\chrome.exe`）の明示的指定
   - ログインページの要素検出を改善（複数セレクタ対応）
   - 記事作成ページへの正しい遷移（`https://note.com/new`）
   - タイトル・本文入力の柔軟なセレクタ対応（textarea/contenteditable両対応）
   - AIモーダルの自動クローズ
   - 「公開に進む」ボタンの自動検出とクリック
   - 投稿前後のスクリーンショット自動保存機能

4. **実行テスト成功**
   ```bash
   python note_platform/post_note.py "【自動投稿テスト】完全自動化" "これは完全自動化のテストです。"
   ```
   - ✅ 自動ログイン成功
   - ✅ タイトル・本文入力成功
   - ✅ 記事公開成功
   - 📸 スクリーンショット保存: `C:\Users\toshi\note_post_preview.png`, `note_post_after.png`

5. **変更をコミット**
   - コミットID: `704175b`
   - メッセージ: "Windows環境でのNote自動投稿機能を実装"

#### Phase 2完成（X Platform）

**実装した機能**

1. **投稿文生成** (`generate_x.py`)
   - Gemini API統合
   - 280文字制限対応
   - ハッシュタグと絵文字の自動挿入
   - カジュアルで魅力的な文章生成
   - 140文字検索最適化対応

2. **X投稿** (`post_x.py`)
   - Twitter API v2統合
   - Dry runモードでテスト可能
   - 投稿URL自動取得
   - エラーハンドリング

**動作確認済み**

```bash
# 投稿文生成テスト
python x_platform/generate_x.py "Phase 2完成！"
✅ 正常動作確認

# 投稿テスト（Dry run）
python x_platform/post_x.py "テスト" --dry-run
✅ 正常動作確認
```

---

### 2025-01-12

#### プロジェクト立ち上げ

- プロジェクト構想・仕様書作成（SPECIFICATION.md）
- ディレクトリ構造設計
- 技術スタック選定

#### Phase 1完成（Activity DB）

**実装内容**

1. **db.py**（Supabase接続・CRUD）
   - `init_db()`: Supabaseテーブル初期化
   - `add_activity(content)`: 活動追加
   - `get_activity(id)`: ID指定取得
   - `get_latest()`: 最新取得
   - `list_activities()`: 活動一覧取得
   - `delete_activity(id)`: 活動削除

2. **cleanup.py**（データクリーンアップ）
   - `cleanup_old_data(days)`: 古いデータ削除+VACUUM

3. **add_activity.py**（CLI）
   - コマンドラインから活動追加

4. **list_activities.py**（CLI）
   - コマンドラインから活動一覧表示

**成果物**: 活動を保存・取得・削除できるDB

---

## 🛠️ 技術メモ

### Windows環境での注意点

- **Chromeのパス**: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- **UTF-8エンコーディング**: `sys.stdout` の再設定で対応
- **Noteのログインページ**: 動的ロード（`time.sleep(3)`で待機が必要）

### Note.com UIの特徴

- **記事作成URL**: `https://note.com/new`
- **タイトル**: `textarea[placeholder*='タイトル']`
- **本文**: `div[contenteditable='true']`（contenteditable要素）
- **公開ボタン**: テキストに「公開」を含むボタン

### 成功したセレクタパターン

```python
# メール入力
"input[placeholder*='mail']"

# パスワード入力
"input[type='password']"

# ログインボタン
btn.text.strip() == 'ログイン'

# 公開ボタン
'公開' in btn.text.strip()
```

---

## 🔧 データベース変更履歴

### Activity ID形式の変更（2025-10-13）

**変更内容**
- **変更前**: UUID形式（例: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`）
- **変更後**: 5桁数字形式（例: `00001`, `00002`, ...）
- **対応範囲**: 最大99,999件まで対応可能

**理由**
- IDの可読性向上
- コマンドライン操作の簡便化
- URL短縮

**マイグレーション手順**

詳細は `SPECIFICATION.md` の「データベース設計 > ID形式変更」セクションを参照。

---

## 📦 使用技術スタック

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
- undetected-chromedriver (検出回避）

---

## 🎯 動作確認状況

### Phase 1: Activity DB
- [x] DB接続テスト
- [x] 活動追加テスト
- [x] 活動一覧表示テスト
- [x] クリーンアップテスト
- [x] ID形式変更（UUID → 5桁数字）

### Phase 2: X Platform
- [x] 投稿文生成テスト（Gemini API）
- [x] 投稿テスト（Dry run）
- [x] 140文字検索最適化対応
- [ ] 実際のX投稿テスト（オプション）

### Phase 3: Note Platform
- [x] 記事生成テスト（Gemini API）
- [x] 自動ログインテスト
- [x] 記事投稿テスト（Windows環境）
- [x] スクリーンショット保存機能

---

## 🐛 既知の問題・制限事項

### Gemini API警告メッセージ

実行時に以下の警告が表示されますが、動作には影響ありません：
```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
E0000 00:00:... ALTS creds ignored. Not running on GCP...
```

### Note投稿の制限

- Seleniumを使用しているため、ブラウザの表示が必要
- ヘッドレスモードでは動作しない可能性がある
- Note.comのUI変更により、セレクタが動作しなくなる可能性がある

### X API制限

- 無料プランでは投稿回数に制限がある
- Read and Write権限が必要

---

## 📝 今後の改善案

### Phase 4: 統合とスケジューラー

1. **統合実行スクリプト**
   - Activity DB → X投稿 → Note投稿を一括実行
   - エラーハンドリングとリトライ機能

2. **スケジューラー**
   - cron/Windows Task Scheduler対応
   - 定期実行機能

3. **投稿履歴管理**
   - 投稿成功/失敗の記録
   - 投稿済み活動の管理

4. **通知機能**
   - 投稿成功/失敗の通知（メール/Slack）

### その他の改善

- Qiita/Zenn投稿機能の追加
- 投稿テンプレートのカスタマイズ機能
- 画像添付機能
- ハッシュタグの自動最適化

---

## 📚 参考資料

### 外部リンク

- [Supabase公式ドキュメント](https://supabase.com/docs)
- [Gemini API公式ドキュメント](https://ai.google.dev/docs)
- [Twitter API v2公式ドキュメント](https://developer.twitter.com/en/docs/twitter-api)
- [Selenium公式ドキュメント](https://www.selenium.dev/documentation/)

### プロジェクト内ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 全体仕様
- [PROJECT_GUIDE.md](./PROJECT_GUIDE.md) - プロジェクトガイド
- [PROMPTS.md](./PROMPTS.md) - プロンプト集

---

**最終更新**: 2025-10-16
