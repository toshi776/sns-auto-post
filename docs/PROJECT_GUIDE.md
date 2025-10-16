# SNS自動投稿システム - プロジェクトガイド

## 📋 現在の状況

### ✅ 完了したフェーズ

**Phase 1: Activity DB（活動記録）**
- Supabase接続とCRUD操作
- 活動追加CLI（`add_activity.py`）
- 活動一覧表示CLI（`list_activities.py`）
- データクリーンアップ（`cleanup.py`）
- ID形式を5桁数字に変更（`00001`形式）

**Phase 2: X Platform（X投稿）**
- Gemini APIで投稿文生成（`generate_x.py`）
- Twitter APIでX投稿（`post_x.py`）
- 140文字検索最適化対応
- Dry runモードでのテスト機能

**Phase 3: Note Platform（Note投稿）**
- Gemini APIで記事生成（`generate_note.py`）
- Note.comへの自動投稿（`post_note.py`）
- Windows環境で動作確認済み
- スクリーンショット自動保存機能

### 📁 プロジェクト構成

```
sns-auto-post/
├── .env                      # 環境変数（設定済み）
├── .env.example              # テンプレート
├── .gitignore                # Git設定
├── README.md                 # プロジェクト概要
├── requirements.txt          # 依存ライブラリ
├── docs/
│   ├── SPECIFICATION.md      # 詳細仕様書
│   ├── PROJECT_GUIDE.md      # 本ファイル
│   ├── DEVELOPMENT.md        # 開発履歴
│   └── PROMPTS.md            # プロンプト集
├── activity_db/              # Phase 1完成
│   ├── __init__.py
│   ├── db.py
│   ├── add_activity.py
│   ├── list_activities.py
│   ├── cleanup.py
│   └── README.md
├── x_platform/               # Phase 2完成
│   ├── __init__.py
│   ├── generate_x.py
│   ├── post_x.py
│   └── README.md
└── note_platform/            # Phase 3完成
    ├── __init__.py
    ├── generate_note.py
    ├── post_note.py
    └── README.md
```

---

## 🚀 次のフェーズ（Phase 4）

### 統合スケジューラーの実装

Phase 4では、全モジュールを統合した自動化スケジューラーを実装予定：

1. **スケジューラーモジュール作成**
   - 定期実行機能（cron/Windows Task Scheduler対応）
   - 設定ファイルでの投稿頻度管理

2. **統合ワークフロー**
   ```
   活動記録 → 記事生成 → X投稿 & Note投稿
   ```
   - Activity DBから最新の活動を取得
   - Gemini APIで記事を自動生成
   - XとNoteに同時投稿

3. **エラーハンドリングと通知**
   - 投稿失敗時のリトライ機能
   - 実行ログの記録
   - 通知機能（オプション）

4. **ドキュメント整備**
   - 全体的な使い方ガイド
   - トラブルシューティング
   - デプロイ手順

---

## 🔄 作業再開手順

### 1. 環境確認

```bash
cd /home/toshi776/projects/sns-auto-post

# 依存ライブラリの確認
pip3 install -r requirements.txt

# .envファイルの確認
ls -la .env
```

### 2. データベース確認

Activity DBが正しく動作しているか確認：

```bash
# 活動一覧を表示
python3 activity_db/list_activities.py

# 新しい活動を追加
python3 activity_db/add_activity.py "テスト活動"
```

### 3. 基本的な使い方

#### 活動を記録してX投稿

```bash
# 1. 活動を記録
python3 activity_db/add_activity.py "今日の活動内容"

# 2. 最新の活動を確認
python3 activity_db/list_activities.py

# 3. X投稿文を生成（Dry run）
cd x_platform
python3 post_x.py --latest --dry-run

# 4. 実際に投稿
python3 post_x.py --latest
```

#### 活動を記録してNote投稿

```bash
# 1. 活動を記録（まだの場合）
python3 activity_db/add_activity.py "今日の活動内容"

# 2. Note記事を生成して投稿
cd note_platform
python3 post_note.py --latest
```

---

## 💡 次回開始時のメッセージ例

Phase 4を開始する場合：
```
Phase 3（Note投稿）が完成しました。
Phase 4（統合スケジューラー）の実装を開始してください。
```

既存機能をテストする場合：
```
X投稿機能とNote投稿機能をテストしたいです。
```

---

## 🎯 プロジェクト全体の進捗

- [x] Phase 1: Activity DB（活動記録）
- [x] Phase 2: X Platform（X投稿）
- [x] Phase 3: Note Platform（Note投稿）
- [ ] Phase 4: 統合とスケジューラー

---

## 📚 参考ドキュメント

- [SPECIFICATION.md](./SPECIFICATION.md) - 全体仕様
- [DEVELOPMENT.md](./DEVELOPMENT.md) - 開発履歴・技術メモ
- [PROMPTS.md](./PROMPTS.md) - プロンプト集
- [activity_db/README.md](../activity_db/README.md) - Activity DB使い方
- [x_platform/README.md](../x_platform/README.md) - X Platform使い方
- [note_platform/README.md](../note_platform/README.md) - Note Platform使い方
- [README.md](../README.md) - プロジェクト概要

---

## 🐛 トラブルシューティング

### Gemini API警告メッセージ

実行時に以下の警告が表示されますが、動作には影響ありません：
```
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
E0000 00:00:... ALTS creds ignored. Not running on GCP...
```

### X API投稿エラー

403エラーが出た場合：
1. X Developer Portalでアプリの権限を確認
2. 「Read and Write」権限が必要
3. 権限変更後、Access Tokenを再生成

### Note投稿エラー

Windows環境での注意点：
- Chromeのパス: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- UTF-8エンコーディングは自動対応済み
- Noteのログインページは動的ロード（3秒待機）

### モジュールが見つからない場合

```bash
pip3 install -r requirements.txt
```

### .envが読み込まれない場合

```bash
# .envファイルがプロジェクトルートにあることを確認
ls -la .env

# パーミッション確認
chmod 600 .env
```

---

## 📅 最終更新

**最終更新日**: 2025-10-16
**次回作業開始時**: このファイルを確認してから作業を再開してください
