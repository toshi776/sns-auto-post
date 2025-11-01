# ZennのGitHub連携セットアップ手順

このドキュメントでは、ZennのGitHub連携を使った自動投稿のセットアップ方法を説明します。

## 📋 目次

1. [前提条件](#前提条件)
2. [GitHubリポジトリの作成](#ステップ1-githubでリポジトリを作成)
3. [Zenn CLIで初期セットアップ](#ステップ2-zenn-cliで初期セットアップ推奨)
4. [Zennでリポジトリを連携](#ステップ3-zennでリポジトリを連携)
5. [環境変数の設定](#ステップ4-envファイルに設定を追加)
6. [テスト投稿](#ステップ5-テスト投稿dry-run)
7. [実際に投稿](#ステップ6-実際に投稿してみる)
8. [統合ファイルでの投稿](#統合ファイルでの投稿方法)
9. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

- GitHubアカウント
- Zennアカウント
- Git がインストールされていること
- Node.js がインストールされていること（Zenn CLI使用のため）
- Python環境がセットアップされていること

---

## ステップ1: GitHubでリポジトリを作成

### 1-1. GitHubにアクセス
- https://github.com にログイン

### 1-2. 新しいリポジトリを作成
1. 右上の「+」→「New repository」をクリック
2. Repository name: `zenn-content`（お好みの名前でOK）
3. Public/Private: お好みで選択（どちらでもOK）
4. 「Add a README file」にチェック（推奨）
5. 「Create repository」をクリック

---

## ステップ2: Zenn CLIで初期セットアップ（推奨）

ローカルでリポジトリを準備します。

### 2-1. リポジトリをクローン

お好みの場所にクローンします（例: `C:\Projects`）

```bash
# お好みの場所に移動
cd C:\Projects

# リポジトリをクローン（あなたのGitHubユーザー名に置き換えてください）
git clone https://github.com/あなたのユーザー名/zenn-content
cd zenn-content
```

### 2-2. Zenn CLIをインストール

```bash
# package.jsonを作成
npm init --yes

# Zenn CLIをインストール
npm install zenn-cli
```

### 2-3. Zennの初期セットアップ

```bash
# Zennの初期化
npx zenn init
```

これで以下のディレクトリ構造が作成されます：

```
zenn-content/
├── articles/          ← 記事ファイルを配置するディレクトリ
├── books/            ← 本のファイルを配置（今回は使用しない）
├── node_modules/
├── .gitignore
├── package.json
└── README.md
```

### 2-4. GitHubにプッシュ

```bash
git add .
git commit -m "Initial setup with Zenn CLI"
git push
```

---

## ステップ3: Zennでリポジトリを連携

### 3-1. Zennのダッシュボードにアクセス
- https://zenn.dev/dashboard/deploys にアクセス

### 3-2. リポジトリを連携
1. 「リポジトリを連携する」ボタンをクリック
2. GitHubの認証画面が表示されたら許可
3. 先ほど作成した`zenn-content`リポジトリを選択
4. 「連携する」をクリック

### 3-3. 連携ブランチを確認
- デフォルトは`main`ブランチ
- このブランチにプッシュすると自動的にZennに反映されます

---

## ステップ4: .envファイルに設定を追加

プロジェクトのルートディレクトリ（`C:\Project\sns-auto-post`）で、`.env`ファイルを編集します。

### 4-1. .envファイルに追加

ファイルの最後に以下を追加：

```bash
# Zenn GitHub連携設定
ZENN_GITHUB_REPO_PATH=C:\Projects\zenn-content
```

**パスの例:**
- `C:\Projects\zenn-content`
- `C:\Users\toshi\Documents\zenn-content`
- `/home/user/zenn-content` (Linux/Mac)

**重要:** クローンした実際のパスに置き換えてください。

---

## ステップ5: テスト投稿（Dry run）

まず、dry runモードでテストします。

### 5-1. テストコマンド実行

```bash
python main.py --zenn-title "ZennのGitHub連携テスト" \
               --zenn-content "# はじめに\n\nこれはテスト記事です。" \
               --zenn-emoji "🧪" \
               --zenn-topics Python Test \
               --zenn-type tech \
               --zenn-github \
               --dry-run
```

### 5-2. 期待される出力

```
🔍 [DRY RUN] 実際には投稿しません
  スラッグ: zenn-20251101-100000
  タイトル: ZennのGitHub連携テスト
  本文の長さ: 39文字
  絵文字: 🧪
  タイプ: tech
  トピック: Python, Test
  公開: はい

✅ Zenn投稿 [DRY RUN] 完了
```

---

## ステップ6: 実際に投稿してみる

Dry runが成功したら、`--dry-run`を外して実際に投稿します。

### 6-1. 投稿コマンド実行

```bash
python main.py --zenn-title "ZennのGitHub連携テスト" \
               --zenn-content "# はじめに\n\nこれはテスト記事です。GitHub連携で自動投稿しています。\n\n## まとめ\n\n自動投稿に成功しました！" \
               --zenn-emoji "🧪" \
               --zenn-topics Python Test GitHub \
               --zenn-type tech \
               --zenn-github
```

### 6-2. 何が起こるか

1. `zenn-content/articles/`に`.md`ファイルが作成されます
2. Gitでコミットされます
3. GitHubにプッシュされます
4. 数分後、Zennに記事が自動的に表示されます

### 6-3. 期待される出力

```
⚡ Zenn に投稿中（GitHub連携方式）...
================================================================================
📝 記事ファイルを作成: zenn-20251101-100000.md
🔄 Gitでコミット・プッシュ中...
⬆️  GitHubにプッシュ中...
✅ GitHubへのプッシュ完了
📄 記事ファイル: C:\Projects\zenn-content\articles\zenn-20251101-100000.md
🔄 Zennが自動的に記事を同期します（数分かかる場合があります）

✅ Zenn投稿完了（GitHub連携）
```

---

## ステップ7: Zennで確認

### 7-1. デプロイログを確認

- https://zenn.dev/dashboard/deploys
- 最新のデプロイ状況が表示されます
- ✅成功マークが表示されればOK
- ⚠️エラーがある場合は、エラーメッセージを確認

### 7-2. 記事を確認

- https://zenn.dev/dashboard
- ダッシュボードの「記事」タブで新しい記事が表示されます
- 公開設定によって、公開記事または下書きとして表示されます

### 7-3. 記事を公開・編集

- 下書きの場合は「公開する」ボタンで公開できます
- Zennのエディタで編集することも可能
- ローカルのマークダウンファイルを編集してプッシュすることも可能

---

## 統合ファイルでの投稿方法

すべてのプラットフォーム（X、Note、Qiita、Zenn）に一括投稿する場合。

### 投稿ファイル作成

`posts/post.txt` を作成します：

```
[X]
ZennのGitHub連携で記事を自動投稿するシステムを作りました！ #Python #Zenn #自動化

[Note Title]
ZennのGitHub連携で記事を自動投稿するシステムを作ってみた

[Note Content]
# はじめに

Zennの記事をGitHub経由で自動投稿できるシステムを作成しました。

## 使用技術
- Python
- GitHub Actions
- Zenn CLI

## まとめ
GitHub連携により、記事のバージョン管理と自動投稿が実現できました。

[Qiita Title]
ZennのGitHub連携で記事を自動投稿するシステムを作ってみた

[Qiita Content]
# はじめに

Zennの記事をGitHub経由で自動投稿できるシステムを作成しました。

## 使用技術
- Python
- GitHub Actions
- Zenn CLI

## まとめ
GitHub連携により、記事のバージョン管理と自動投稿が実現できました。

[Qiita Tags]
Python, Zenn, GitHub, 自動化

[Zenn Title]
ZennのGitHub連携で記事を自動投稿するシステムを作ってみた

[Zenn Content]
# はじめに

Zennの記事をGitHub経由で自動投稿できるシステムを作成しました。

## 使用技術
- Python
- GitHub Actions
- Zenn CLI

## まとめ
GitHub連携により、記事のバージョン管理と自動投稿が実現できました。

[Zenn Emoji]
🚀

[Zenn Topics]
Python, GitHub, Zenn, 自動化
```

### 投稿コマンド

```bash
# Dry runでテスト
python main.py --post-file "posts/post.txt" --zenn-github --dry-run

# 実際に投稿
python main.py --post-file "posts/post.txt" --zenn-github
```

---

## コマンドラインオプション

### Zenn投稿の主要オプション

| オプション | 説明 | 必須 | デフォルト |
|-----------|------|------|-----------|
| `--zenn-title` | 記事のタイトル | ✅ | - |
| `--zenn-content` | 記事の本文（直接指定） | ※1 | - |
| `--zenn-content-file` | 記事の本文ファイルパス | ※1 | - |
| `--zenn-emoji` | 絵文字アイコン（1文字） | ❌ | 📝 |
| `--zenn-topics` | トピック（最大5個） | ❌ | - |
| `--zenn-type` | 記事タイプ（tech/idea） | ❌ | tech |
| `--zenn-slug` | スラッグ（12-50文字） | ❌ | 自動生成 |
| `--zenn-draft` | 下書きとして保存 | ❌ | false |
| `--zenn-github` | GitHub連携方式を使用 | ✅ | false |
| `--dry-run` | 実際には投稿しない | ❌ | false |

※1: `--zenn-content`または`--zenn-content-file`のいずれかが必須

### 使用例

```bash
# 基本的な投稿
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-github

# 詳細なオプション指定
python main.py --zenn-title "詳細な記事タイトル" \
               --zenn-content-file "content.md" \
               --zenn-emoji "🎉" \
               --zenn-type tech \
               --zenn-topics Python GitHub Zenn 自動化 API \
               --zenn-slug "my-custom-article-slug" \
               --zenn-github

# 下書きとして保存
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-draft \
               --zenn-github

# Dry runモード
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-github \
               --dry-run
```

---

## トラブルシューティング

### エラー1: `ZENN_GITHUB_REPO_PATHが設定されていません`

**原因:**
- `.env`ファイルに`ZENN_GITHUB_REPO_PATH`が設定されていない

**解決方法:**
1. `.env`ファイルを開く
2. 以下を追加：
   ```bash
   ZENN_GITHUB_REPO_PATH=C:\Projects\zenn-content
   ```
3. パスを実際のクローン先に置き換える

---

### エラー2: `指定されたリポジトリパスが存在しません`

**原因:**
- 指定したパスが間違っている
- リポジトリがクローンされていない

**解決方法:**
1. パスが正しいか確認
2. リポジトリが実際にクローンされているか確認
3. パスに日本語や空白が含まれていないか確認

```bash
# パスの確認方法（Windows）
dir C:\Projects\zenn-content

# パスの確認方法（Linux/Mac）
ls -la /path/to/zenn-content
```

---

### エラー3: `git add失敗` / `git commit失敗` / `git push失敗`

**原因:**
- Git設定が不完全
- リポジトリへの書き込み権限がない
- GitHubの認証が失敗している

**解決方法:**

1. **Git設定を確認**
   ```bash
   git config --global user.name
   git config --global user.email
   ```

2. **設定されていない場合は設定**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

3. **GitHubの認証確認**
   ```bash
   cd C:\Projects\zenn-content
   git push
   ```
   - ユーザー名/パスワードを求められる場合は入力
   - Personal Access Tokenが必要な場合は取得して使用

4. **リモートURLを確認**
   ```bash
   git remote -v
   ```

---

### エラー4: Zennに記事が表示されない

**原因:**
- デプロイに失敗している
- 同期に時間がかかっている
- リポジトリ連携が正しくない

**解決方法:**

1. **デプロイログを確認**
   - https://zenn.dev/dashboard/deploys にアクセス
   - エラーメッセージがあれば内容を確認

2. **時間を置いて再確認**
   - 同期に数分かかる場合があります
   - 5-10分待ってから再度確認

3. **リポジトリ連携を再確認**
   - https://zenn.dev/dashboard/deploys で連携状態を確認
   - 必要に応じて再連携

4. **記事ファイルの形式を確認**
   - フロントマターが正しいか確認
   - YAMLの文法エラーがないか確認

---

### エラー5: スラッグの文字数制限エラー

**原因:**
- スラッグが12文字未満または50文字を超えている

**解決方法:**
- スラッグを指定しない（自動生成に任せる）
- または12-50文字の範囲で指定

```bash
# スラッグを指定しない（推奨）
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-github

# スラッグを手動指定
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-slug "my-article-2024-11-01" \
               --zenn-github
```

---

### エラー6: トピックが多すぎる

**原因:**
- トピックが5個を超えている

**解決方法:**
- トピックを5個以内に制限

```bash
# OK: トピック5個以内
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-topics Python GitHub Zenn API 自動化 \
               --zenn-github

# NG: トピック6個
python main.py --zenn-title "タイトル" \
               --zenn-content-file "content.md" \
               --zenn-topics Python GitHub Zenn API 自動化 Test \
               --zenn-github
```

---

## よくある質問（FAQ）

### Q1: GitHub連携方式とSelenium方式の違いは？

**GitHub連携方式（推奨）:**
- ✅ 公式サポート、安定動作
- ✅ Googleアカウントでも利用可能
- ✅ バージョン管理が可能
- ✅ ブラウザ不要
- ❌ 初期セットアップがやや複雑

**Selenium方式:**
- ✅ セットアップが簡単
- ❌ メール/パスワード認証が必要
- ❌ ブラウザ操作が必要
- ❌ 不安定な場合がある

### Q2: 既存の記事を更新できますか？

はい、できます。

1. 同じスラッグのファイルを再度プッシュ
2. Zennが自動的に記事を更新します

```bash
# 同じスラッグで再投稿
python main.py --zenn-title "更新されたタイトル" \
               --zenn-content-file "updated-content.md" \
               --zenn-slug "existing-article-slug" \
               --zenn-github
```

### Q3: 記事を削除するには？

記事の削除はZennのダッシュボードから行う必要があります。

1. https://zenn.dev/dashboard にアクセス
2. 削除したい記事を選択
3. 「削除」ボタンをクリック

**注意:** GitHubからファイルを削除しても、Zenn側の記事は削除されません。

### Q4: 画像はどうやってアップロードしますか？

ZennのGitHub連携では、以下の方法で画像を使用できます：

1. **外部画像サービスを使用**
   - Imgur、Cloudinaryなどにアップロード
   - URLをマークダウンに記載

2. **GitHubリポジトリに配置**
   - `images/`ディレクトリを作成
   - 画像を配置してプッシュ
   - 相対パスで参照: `![画像](../images/sample.png)`

### Q5: 複数のリポジトリを連携できますか？

Zennでは最大2つのリポジトリを連携できます。

---

## 参考リンク

- [Zenn公式: GitHubリポジトリ連携](https://zenn.dev/zenn/articles/connect-to-github)
- [Zenn CLI使い方](https://zenn.dev/zenn/articles/zenn-cli-guide)
- [Zennのマークダウン記法](https://zenn.dev/zenn/articles/markdown-guide)

---

**作成日**: 2025-11-01
**最終更新**: 2025-11-01
