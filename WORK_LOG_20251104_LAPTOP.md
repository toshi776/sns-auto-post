# 作業ログ - ノートパソコンでのセットアップと投稿

**日付**: 2025-11-04（ノートパソコン）
**作業者**: Claude Code + toshi776

## 📋 実施内容

### 1. ノートパソコンでの環境セットアップ

自宅ではなくノートパソコンで作業を開始したため、zenn-content環境を再構築しました。

#### zenn-content環境の構築

```bash
# GitHubからクローン
git clone https://github.com/toshi776/zenn-content.git

# npm依存関係のインストール
cd zenn-content
npm install
```

#### .env設定の追加

```bash
# Zenn（GitHub連携方式）
ZENN_GITHUB_REPO_PATH=C:\Project\sns-auto-post\zenn-content
```

#### Git設定

```bash
cd zenn-content
git config user.email "toshi776@gmail.com"
git config user.name "toshi776"
```

---

### 2. エンコーディング問題の修正

Bashツールから実行する際に`sys.stdout`/`sys.stderr`の再設定が競合してエラーが発生する問題を修正しました。

#### 修正したファイル

1. **zenn_platform/post_zenn_github.py** - sys.stdout/stderr再設定をコメントアウト
2. **zenn_platform/post_zenn.py** - sys.stdout/stderr再設定をコメントアウト
3. **qiita_platform/post_qiita.py** - sys.stdout/stderr再設定をコメントアウト
4. **note_platform/post_note.py** - sys.stdout/stderr再設定をコメントアウト
5. **main.py** - `reconfigure()`を使った安全なUTF-8設定を追加

#### 修正内容（main.py）

```python
# Windows環境でのUTF-8出力設定（reconfigureを使用）
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
```

---

### 3. 本番投稿テスト

LINE業務報告自動化システムの記事を各プラットフォームに投稿しました。

#### 投稿結果

| プラットフォーム | ステータス | URL |
|---|---|---|
| **X (Twitter)** | ✅ 成功 | https://x.com/toshi776/status/1985547360999784977 |
| **Note** | ✅ 成功 | https://note.com/toshi776/n/n84be93c5fd63 |
| **Qiita** | ✅ 成功 | https://qiita.com/toshi776/items/ed9da92d55bf1976f5e8 |
| **Zenn** | ✅ 成功 | GitHub連携で投稿（articles/python-yaml-line.md） |

#### 投稿内容

- **タイトル**: PythonとYAMLで作るLINE業務報告自動化システム
- **タグ**: Python, YAML, 自動化, LINE
- **本文**: 911文字（Qiita/Zenn）、672文字（Note）

---

### 4. Qiita投稿の問題と修正

#### 問題

最初の投稿で、`--qiita-content-file posts/post.txt`を使用したため、posts.txtファイル全体（X、Note、Qiita、Zennの全セクション）がQiita本文として投稿されてしまいました。

#### 解決策

Qiita専用の投稿ファイル `posts/qiita_only.txt` を作成し、`[Qiita Title]`、`[Qiita Content]`、`[Qiita Tags]`セクションのみを含めました。

```bash
python main.py --post-file posts/qiita_only.txt
```

結果：正しい内容でQiitaに再投稿成功

---

## 🔧 技術的な詳細

### エラー解決の流れ

1. **ValueError: I/O operation on closed file**
   - 原因: Bashツールと`sys.stdout`/`sys.stderr`再設定の競合
   - 解決: 各モジュールの再設定コードをコメントアウト

2. **UnicodeEncodeError: 'cp932' codec can't encode**
   - 原因: main.pyにUTF-8設定がなかった
   - 解決: `reconfigure()`を使った安全な設定を追加

3. **git commit失敗: Author identity unknown**
   - 原因: zenn-contentリポジトリにGitユーザー設定がなかった
   - 解決: `git config user.email/user.name`を設定

4. **Qiita API Error (Status 400)**
   - 原因1: タグが正しく渡されていなかった
   - 原因2: `--qiita-content-file`で全ファイル内容を投稿
   - 解決: `--post-file`でセクション形式を使用 + qiita_only.txt作成

---

## 📁 作成・更新されたファイル

### 新規作成
- `posts/qiita_only.txt` - Qiita専用投稿ファイル
- `WORK_LOG_20251104_LAPTOP.md` - 本ログファイル

### 更新されたファイル
- `main.py` - UTF-8エンコーディング設定追加
- `zenn_platform/post_zenn_github.py` - エンコーディング設定コメントアウト
- `zenn_platform/post_zenn.py` - エンコーディング設定コメントアウト
- `qiita_platform/post_qiita.py` - エンコーディング設定コメントアウト
- `note_platform/post_note.py` - エンコーディング設定コメントアウト
- `.env` - ZENN_GITHUB_REPO_PATH追加

---

## ✅ 動作確認済み

- [x] Zenn dry-runテスト成功
- [x] X投稿成功
- [x] Note投稿成功
- [x] Qiita投稿成功
- [x] Zenn投稿成功（GitHub連携）

---

## 📝 今後の作業（自宅で継続）

- 追加の投稿テスト
- その他の機能改善

---

## 🎯 重要な学び

1. **統合ファイル形式の使い方**
   - `--post-file`でセクション形式を使うと、各プラットフォームに正しく分配される
   - `--content-file`を使うとファイル全体が投稿される

2. **ノートパソコンでの環境再現**
   - zenn-contentのクローンとnpm install
   - Git設定（user.email, user.name）
   - .env設定（ZENN_GITHUB_REPO_PATH）

3. **エンコーディング問題**
   - Bashツールから実行する場合、`sys.stdout`再設定は不要
   - `reconfigure()`を使うのが安全

---

**次回の作業**: 自宅環境で作業を継続します。
