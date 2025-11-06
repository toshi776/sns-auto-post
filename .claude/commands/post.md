---
description: content_*.txt を読み込み、各プラットフォーム専用ファイルを生成して投稿
---

# SNS自動投稿コマンド

以下の手順で投稿を実行してください：

## 1. ファイルの確認
- `posts/` フォルダから最新の `content_YYYY-MM-DD.txt` を探す
- 複数ある場合はユーザーに選択してもらう

## 2. ファイルの読み込みと解析
- `content_YYYY-MM-DD.txt` の内容を読み込む
- 既存のセクションを確認：
  - [X]
  - [Note Title] / [Note Content]
  - [Qiita Title] / [Qiita Content] / [Qiita Tags]
  - [Zenn Title] / [Zenn Content] / [Zenn Topics] / [Zenn Emoji]
  - [Blog Title] / [Blog Content]

## 3. プラットフォーム専用ファイルの生成

### 3-1. X投稿用ファイル（x_only.txt）
- [X]セクションの内容を取得
- マークダウン記号を除去：
  - `**太字**` → 太字
  - `- 箇条書き` → ・箇条書き または 適切な改行
  - コードブロック記号（```）を削除
  - その他のマークダウン記法を一般的な表現に変換
- 読みやすく整形（改行、スペースを適切に配置）
- `posts/x_only.txt` に書き込み

### 3-2. Qiita投稿用ファイル（qiita_only.txt）
- [Qiita Title]、[Qiita Content] を取得
- [Qiita Tags] が不足している場合は自動生成：
  - 技術的なキーワード（具体的な技術名、ツール名、言語名）
  - 最大5個
  - カンマ区切り
  - 例: `clasp, GoogleAppsScript, WSL2, OAuth, 環境構築`
- 完全な形式で `posts/qiita_only.txt` に書き込み：
  ```
  [Qiita Title]
  タイトル

  [Qiita Content]
  本文

  [Qiita Tags]
  tag1, tag2, tag3
  ```

### 3-3. Zenn投稿用ファイル（zenn_only.txt）
- [Zenn Title]、[Zenn Content] を取得
- 不足セクションを補完：
  - [Zenn Topics]（最大5個、小文字推奨）
  - [Zenn Emoji]（記事内容に合った絵文字1文字、デフォルト: 📝）
- 完全な形式で `posts/zenn_only.txt` に書き込み：
  ```
  [Zenn Title]
  タイトル

  [Zenn Content]
  本文

  [Zenn Topics]
  topic1, topic2, topic3

  [Zenn Emoji]
  📝
  ```

### 3-4. Note・Blog投稿
- Noteは `content_YYYY-MM-DD.txt` をそのまま使用
- Blogも `content_YYYY-MM-DD.txt` をそのまま使用

## 4. 投稿実行
生成したファイルを使って投稿：
```bash
python main.py --post-file "posts/content_YYYY-MM-DD.txt"
```

※X、Qiita、Zennについては、システムが自動的に *_only.txt ファイルを優先的に読み込む仕組みが必要
→ 実際には、個別に投稿コマンドを実行する方が確実

実行コマンド例：
```bash
# X投稿
python main.py --x-text-file "posts/x_only.txt"

# Note投稿
python main.py --post-file "posts/content_YYYY-MM-DD.txt"

# Qiita投稿
python main.py --post-file "posts/qiita_only.txt"

# Zenn投稿
python main.py --post-file "posts/zenn_only.txt" --zenn-github

# Blog投稿
python main.py --post-file "posts/content_YYYY-MM-DD.txt"
```

## 5. 結果の報告
- 各プラットフォームの投稿結果（成功/失敗）
- 投稿先URL
- エラーがあれば詳細を報告

## 重要な注意事項
- 元の `content_YYYY-MM-DD.txt` は絶対に変更しない（読み取り専用）
- 各プラットフォーム専用ファイル（*_only.txt）のみを生成・更新
- 既存の *_only.txt は上書きして問題なし
