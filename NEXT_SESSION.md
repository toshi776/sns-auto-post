# 次回作業開始時のガイド

**作成日**: 2025-11-04
**次回作業予定**: 2025-11-05

---

## 🚀 作業再開手順

### 1. 環境の確認

```bash
# 作業ディレクトリに移動
cd D:\DevProjects\sns-auto-post

# 最新の状態を取得
git pull origin main

# zenn-contentも更新
cd zenn-content
git pull origin main
cd ..

# Python環境の確認
python --version  # Python 3.10以上

# Git状態の確認
git status
```

---

### 2. 前回までの作業内容を確認

以下のログファイルを参照してください：

- **WORK_LOG_20251104.md** - 午前：Zenn環境セットアップ
- **WORK_LOG_20251104_LAPTOP.md** - ノートPCでの作業
- **WORK_LOG_20251104_PM.md** - 午後：Zenn投稿完成と調整

---

## ✅ 現在の状態

### 完成している機能

1. ✅ **X (Twitter) 自動投稿** - API経由で投稿
2. ✅ **Note.com 自動投稿** - Selenium経由で投稿
3. ✅ **Qiita 自動投稿** - API経由で投稿
4. ✅ **Zenn 自動投稿** - GitHub連携で投稿

### セットアップ済み

- [x] zenn-content リポジトリ作成 & GitHubと連携
- [x] ZennとGitHubリポジトリの連携完了
- [x] 各プラットフォーム専用投稿ファイルの作成
- [x] エンコーディング問題の修正
- [x] 本番投稿のテスト成功

---

## 📁 ファイル構成

### 投稿ファイル（posts/）

```
posts/
├── post.txt          # 統合ファイル（全プラットフォーム）
├── qiita_only.txt    # Qiita専用
├── zenn_only.txt     # Zenn専用
└── zenn_test.txt     # テスト用
```

### Zenn記事（zenn-content/articles/）

```
zenn-content/articles/
└── python-yaml-line.md  # 本番記事
```

---

## 🎯 基本的な使い方

### Zennに投稿する

```bash
# Zenn専用ファイルで投稿
python main.py --post-file posts/zenn_only.txt --zenn-github

# Dry-runでテスト（実際には投稿しない）
python main.py --post-file posts/zenn_only.txt --zenn-github --dry-run
```

### Qiitaに投稿する

```bash
# Qiita専用ファイルで投稿
python main.py --post-file posts/qiita_only.txt

# Dry-runでテスト
python main.py --post-file posts/qiita_only.txt --dry-run
```

### すべてのプラットフォームに一括投稿

```bash
# 統合ファイルで投稿
python main.py --post-file posts/post.txt --zenn-github
```

---

## 📝 投稿ファイルの形式

### Zenn専用ファイル（posts/zenn_only.txt）

```
[Zenn Title]
記事のタイトル

[Zenn Content]
## はじめに

記事の本文（マークダウン形式）

* 箇条書き1
* 箇条書き2

[Zenn Emoji]
📝

[Zenn Topics]
Python, GitHub, 自動化
```

### Qiita専用ファイル（posts/qiita_only.txt）

```
[Qiita Title]
記事のタイトル

[Qiita Content]
## はじめに

記事の本文（マークダウン形式）

[Qiita Tags]
Python, API, 自動化
```

### 統合ファイル（posts/post.txt）

```
[X]
X投稿のテキスト

[Note Title]
Noteのタイトル

[Note Content]
Noteの本文

[Qiita Title]
Qiitaのタイトル

[Qiita Content]
Qiitaの本文

[Qiita Tags]
Python, API

[Zenn Title]
Zennのタイトル

[Zenn Content]
Zennの本文

[Zenn Emoji]
📝

[Zenn Topics]
Python, GitHub
```

---

## 🔧 トラブルシューティング

### 問題1: Zennに記事が表示されない

**確認事項**:
1. GitHubにプッシュされているか確認
   ```bash
   cd zenn-content
   git log --oneline -3
   ```

2. Zennのデプロイ状態を確認
   - https://zenn.dev/dashboard/deploys

3. 1-3分待ってから再確認

**解決策**:
- 空コミットでデプロイを再トリガー
  ```bash
  cd zenn-content
  git commit --allow-empty -m "Trigger deploy"
  git push origin main
  ```

---

### 問題2: エンコーディングエラー

**症状**: `UnicodeEncodeError: 'cp932' codec can't encode`

**解決策**:
- `main.py`に既にUTF-8設定が追加されています
- 問題が発生した場合は、各モジュールのエンコーディング設定を確認

---

### 問題3: Git push失敗

**症状**: `Updates were rejected because the remote contains work`

**解決策**:
```bash
git pull origin main
git push origin main
```

---

## 📍 重要なリンク

### プロジェクトリポジトリ
- sns-auto-post: https://github.com/toshi776/sns-auto-post
- zenn-content: https://github.com/toshi776/zenn-content

### 管理画面
- Zenn記事一覧: https://zenn.dev/dashboard/articles
- Zennデプロイ履歴: https://zenn.dev/dashboard/deploys
- Qiita記事一覧: https://qiita.com/toshi776/items
- Note記事一覧: https://note.com/toshi776/

### ドキュメント
- Zenn公式ドキュメント: https://zenn.dev/zenn/articles/zenn-cli-guide
- Qiita API v2: https://qiita.com/api/v2/docs

---

## 🎯 次回やること（提案）

### すぐできること
- [ ] 新しい記事の投稿テスト
- [ ] 下書き機能のテスト（`--zenn-draft`オプション）
- [ ] 投稿ファイルのテンプレート整備

### 改善案
- [ ] 投稿履歴の記録機能
- [ ] エラーログの保存
- [ ] 画像アップロード対応
- [ ] スケジュール投稿機能
- [ ] 投稿前のプレビュー機能

---

## ⚠️ 注意事項

### 環境変数（.env）
**.envファイルはGit管理外**なので、別のマシンで作業する場合は再設定が必要です。

必要な環境変数:
```bash
# X (Twitter) API
X_API_KEY=...
X_API_SECRET=...
X_ACCESS_TOKEN=...
X_ACCESS_TOKEN_SECRET=...

# Note.com
NOTE_EMAIL=...
NOTE_PASSWORD=...
NOTE_USERNAME=...

# Qiita
QIITA_ACCESS_TOKEN=...

# Zenn（GitHub連携）
ZENN_GITHUB_REPO_PATH=D:\DevProjects\sns-auto-post\zenn-content

# Gemini（オプション）
GEMINI_API_KEY=...
```

---

## 💡 Tips

### 1. Dry-runを活用
本番投稿前に必ず`--dry-run`でテストしましょう。

```bash
python main.py --post-file posts/zenn_only.txt --zenn-github --dry-run
```

### 2. Git状態を常に確認
```bash
git status       # 変更状態の確認
git log -3       # 最近のコミット確認
```

### 3. Zennのデプロイを確認
プッシュ後は必ずデプロイ状態を確認：
https://zenn.dev/dashboard/deploys

---

**次回の作業、頑張ってください！🚀**

何か問題があれば、作業ログを参照するか、GitHubのコミット履歴を確認してください。
