# toshi776技術ブログ - 記事管理

このディレクトリは toshi776.com/blog の記事を管理します。

## ディレクトリ構造

```
toshi776-blog/
├── articles/           # マークダウン記事ファイル
├── templates/          # HTMLテンプレート
├── build/             # ビルド済みHTML（生成される）
└── README.md
```

## 記事の追加方法

1. `articles/` ディレクトリに新しいマークダウンファイルを作成
2. ファイル名形式: `YYYYMMDD-slug.md` (例: `20250110-new-article.md`)
3. ファイルの先頭にメタデータを記述:

```markdown
---
title: 記事のタイトル
date: 2025-01-10
description: 記事の説明文
tags: [AI, DX, 技術]
---

# 記事の本文

マークダウンで記事を書く...
```

## ビルドとデプロイ

```bash
# ブログをビルド（HTML生成）
python blog_platform/build_blog.py

# FTPでアップロード
python blog_platform/deploy_blog.py

# または統合コマンドで
python main.py --post-file posts/blog_test.txt
```
