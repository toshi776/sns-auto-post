# 作業ログ - Zenn自動投稿の完成と調整

**日付**: 2025-11-04（午後）
**作業者**: Claude Code + toshi776
**前回の続き**: WORK_LOG_20251104.md（午前：Zenn環境セットアップ）

---

## 📋 本日午後の作業内容

### 1. GitHubからの最新変更の取得

ノートパソコンで行った作業を自宅環境に反映しました。

```bash
git pull origin main
```

**取得したコミット**:
- `9bf685a` - ノートパソコン環境でのセットアップとエンコーディング問題の修正

**主な変更内容**:
- エンコーディング問題の修正（各モジュールで`sys.stdout`再設定をコメントアウト）
- `main.py`に`reconfigure()`を使った安全なUTF-8設定を追加
- 本番投稿の成功（X、Note、Qiita、Zennすべて投稿成功）
- `posts/qiita_only.txt`の追加
- `WORK_LOG_20251104_LAPTOP.md`の追加

---

### 2. Zenn記事の投稿確認と問題解決

#### 問題1: 記事が投稿されていない

**症状**:
- GitHubにはファイルがプッシュされている
- Zennに記事が表示されない

**原因**:
- ZennとGitHubリポジトリの連携が完了していなかった
- 連携後、デプロイがトリガーされていなかった

**解決手順**:

1. **Zennダッシュボードで連携確認**
   - https://zenn.dev/dashboard/deploys にアクセス
   - 「GitHubリポジトリと連携する」ボタンをクリック
   - GitHub認証 → `toshi776/zenn-content`を選択
   - 連携完了

2. **空コミットでデプロイをトリガー**
   ```bash
   cd zenn-content
   git commit --allow-empty -m "Trigger Zenn deploy after repository connection"
   git pull origin main  # ノートPCからの変更をマージ
   git push origin main
   ```

3. **結果**
   - ✅ デプロイ成功
   - ✅ 3つの記事がZennに表示された

---

#### 問題2: XやNoteのコンテンツも含まれている

**症状**:
Zennの記事に、統合ファイル（`posts/post.txt`）の全セクションが含まれてしまっている：
```
[X]
LINE業務報告を自動化するシステムを開発しました！...

[Note Title]
...

[Qiita Title]
...

[Zenn Content]
...
```

**原因**:
統合ファイル（`posts/post.txt`）をそのまま使用してZenn投稿を実行したため、全セクションが記事本文に含まれてしまった。

**解決策**:
Qiitaと同様に、**Zenn専用の投稿ファイル**を作成する。

**実施内容**:

1. **Zenn専用ファイルを作成**: `posts/zenn_only.txt`
   ```
   [Zenn Title]
   PythonとYAMLで作るLINE業務報告自動化システム

   [Zenn Content]
   ## はじめに
   ...

   [Zenn Emoji]
   📝

   [Zenn Topics]
   Python, YAML, 自動化, LINE
   ```

2. **既存記事を上書き投稿**
   ```bash
   python main.py --post-file posts/zenn_only.txt --zenn-slug python-yaml-line --zenn-github
   ```

3. **結果**
   - ✅ Zennコンテンツのみが含まれた記事に修正された
   - ✅ XやNoteのセクションは削除された

---

#### 問題3: マークダウンが正しく表示されていない？

**症状**:
ユーザーから「マークダウンがそのまま表示されている」という報告。

**原因**:
Zennの**編集画面**を見ていた。編集画面では生のマークダウンが表示される。

**解決**:
「表示を確認」（プレビュー）ボタンを押すことで、正しくレンダリングされた記事が表示されることを確認。

**確認結果**:
- ✅ `##` → 大きな見出しとして表示
- ✅ `*` → 箇条書き（・）として表示
- ✅ コードブロックは背景色付きで表示

---

### 3. 不要なファイルの整理とGitHubへのプッシュ

#### zenn-contentリポジトリの整理

**削除したファイル**:
- `articles/zenn-python-20251104-093554.md` （テスト記事1）
- `articles/zenn-python-20251104-093611.md` （テスト記事2）

**残したファイル**:
- `articles/python-yaml-line.md` （本番記事）

**コミット**: `f0ea45f` - テスト記事ファイルを削除

---

#### sns-auto-postリポジトリの更新

**追加したファイル**:
- `posts/zenn_only.txt` - Zenn専用投稿ファイル

**更新したファイル**:
- `.gitignore` - 一時出力ファイルを除外設定に追加
  ```
  *_output.txt
  note_platform/article*.txt
  ```

**コミット**: `d9b6160` - Zenn専用投稿ファイルを追加

---

## 🎯 完成した機能

### Zenn自動投稿システム（完全版）

#### 使い方

**方法1: Zenn専用ファイルで投稿（推奨）**
```bash
python main.py --post-file posts/zenn_only.txt --zenn-github
```

**方法2: 統合ファイルで全プラットフォームに投稿**
```bash
python main.py --post-file posts/post.txt --zenn-github
```
※ 各プラットフォームのセクションが自動的に分離されます

**方法3: コマンドライン引数で直接指定**
```bash
python main.py \
  --zenn-title "記事タイトル" \
  --zenn-content "記事本文" \
  --zenn-emoji "📝" \
  --zenn-topics Python GitHub 自動化 \
  --zenn-github
```

---

## 📁 現在のファイル構成

### プロジェクト全体
```
sns-auto-post/
├── main.py                          # メインスクリプト
├── .env                             # 環境変数（Git管理外）
├── .gitignore                       # Git除外設定
├── posts/
│   ├── post.txt                    # 統合ファイル（全プラットフォーム）
│   ├── qiita_only.txt              # Qiita専用
│   ├── zenn_only.txt               # Zenn専用（NEW!）
│   └── zenn_test.txt               # テスト用
├── zenn-content/                    # Zenn記事リポジトリ（別Git管理）
│   ├── articles/
│   │   └── python-yaml-line.md    # 本番記事
│   ├── package.json
│   └── .gitignore
├── WORK_LOG_20251104.md            # 午前の作業ログ
├── WORK_LOG_20251104_LAPTOP.md     # ノートPCでの作業ログ
└── WORK_LOG_20251104_PM.md         # 午後の作業ログ（本ファイル）
```

### zenn-contentリポジトリ
```
zenn-content/
├── articles/
│   └── python-yaml-line.md         # 本番記事のみ
├── package.json
├── package-lock.json
└── .gitignore
```

---

## ✅ 動作確認済み

- [x] GitHubからのプル成功
- [x] ZennとGitHubリポジトリの連携成功
- [x] Zennへのデプロイ成功
- [x] Zenn専用ファイルでの投稿成功
- [x] 記事内容の修正成功（XやNoteのセクションを除外）
- [x] マークダウンの正しいレンダリング確認
- [x] 不要なテスト記事の削除
- [x] GitHubへのプッシュ成功

---

## 📊 投稿済みプラットフォーム

本日のノートPC作業で投稿した記事「PythonとYAMLで作るLINE業務報告自動化システム」:

| プラットフォーム | ステータス | URL |
|---|---|---|
| **X (Twitter)** | ✅ 成功 | https://x.com/toshi776/status/1985547360999784977 |
| **Note** | ✅ 成功 | https://note.com/toshi776/n/n84be93c5fd63 |
| **Qiita** | ✅ 成功 | https://qiita.com/toshi776/items/ed9da92d55bf1976f5e8 |
| **Zenn** | ✅ 成功 | GitHub連携（python-yaml-line.md） |

---

## 🔧 技術的な学び

### 1. Zennの仕組み

**デプロイフロー**:
1. `zenn-content/articles/`にマークダウンファイルを配置
2. GitHubにプッシュ
3. Zennが自動的に同期（1-3分）
4. 記事が公開される

**フロントマター**:
```yaml
---
title: "記事タイトル"
emoji: "📝"
type: "tech"  # or "idea"
topics: ["Python", "YAML", "自動化", "LINE"]
published: true  # or false（下書き）
---
```

### 2. 投稿ファイルの使い分け

**統合ファイル（`posts/post.txt`）**:
- すべてのプラットフォームのセクションを含む
- `main.py`が各セクションを自動的に分離
- 一括投稿に便利

**専用ファイル（`posts/qiita_only.txt`、`posts/zenn_only.txt`）**:
- 特定のプラットフォームのみのセクションを含む
- 誤って他のプラットフォームのコンテンツが含まれることを防ぐ
- 単独投稿に推奨

### 3. Zennの編集画面とプレビューの違い

**編集画面**:
- 生のマークダウンが表示される
- `##`、`*`などがそのまま見える

**プレビュー/公開ページ**:
- マークダウンがレンダリングされる
- 見出し、箇条書き、コードブロックが正しく表示される

---

## 🎉 達成したこと

1. ✅ Zenn自動投稿システムの完全動作確認
2. ✅ 統合ファイルと専用ファイルの使い分けの確立
3. ✅ Zenn専用投稿ファイルの作成
4. ✅ テスト記事の整理
5. ✅ すべての変更をGitHubに保存

---

## 📝 次回の作業（明日以降）

### すぐできること

- 新しい記事の投稿テスト
- 各プラットフォームへの投稿練習
- 投稿ファイルのテンプレート作成

### 今後の改善案

- [ ] 投稿履歴の管理機能
- [ ] 下書き保存機能
- [ ] 画像アップロード対応
- [ ] スケジュール投稿機能
- [ ] 投稿結果のログ保存
- [ ] エラーハンドリングの改善

---

## 🚀 使い方クイックリファレンス

### Zenn投稿
```bash
# Zenn専用ファイルで投稿
python main.py --post-file posts/zenn_only.txt --zenn-github

# Dry-runでテスト
python main.py --post-file posts/zenn_only.txt --zenn-github --dry-run
```

### Qiita投稿
```bash
# Qiita専用ファイルで投稿
python main.py --post-file posts/qiita_only.txt

# Dry-runでテスト
python main.py --post-file posts/qiita_only.txt --dry-run
```

### 全プラットフォームに一括投稿
```bash
# 統合ファイルで投稿
python main.py --post-file posts/post.txt --zenn-github
```

---

## 📍 関連リンク

**プロジェクトリポジトリ**:
- sns-auto-post: https://github.com/toshi776/sns-auto-post
- zenn-content: https://github.com/toshi776/zenn-content

**Zenn管理画面**:
- 記事一覧: https://zenn.dev/dashboard/articles
- デプロイ履歴: https://zenn.dev/dashboard/deploys

**投稿済み記事**:
- X: https://x.com/toshi776/status/1985547360999784977
- Note: https://note.com/toshi776/n/n84be93c5fd63
- Qiita: https://qiita.com/toshi776/items/ed9da92d55bf1976f5e8

---

## 💡 重要なポイント

1. **ZennとGitHubの連携は初回のみ必要**
   - 一度連携すれば、以降は自動的に同期される

2. **専用ファイルを使うのが安全**
   - 統合ファイルは便利だが、誤投稿のリスクがある
   - 専用ファイルなら確実に意図したコンテンツのみが投稿される

3. **Zennのデプロイは1-3分かかる**
   - プッシュ後すぐには反映されない
   - デプロイ履歴で状態を確認できる

4. **編集画面とプレビューを混同しない**
   - 編集画面は生のマークダウン
   - プレビュー/公開ページで実際の表示を確認

---

**次回作業時**: このログを参照して、前回の状態から再開してください。

**明日の作業開始時のコマンド**:
```bash
# 最新の状態を取得
git pull origin main
cd zenn-content && git pull origin main && cd ..

# 環境確認
python --version
git status
```

すべて正常に動作しています！🎉
