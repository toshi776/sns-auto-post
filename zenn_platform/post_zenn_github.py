#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenn投稿モジュール（GitHub連携方式）
Gitリポジトリにマークダウンファイルをコミット・プッシュしてZennに記事を投稿
"""

import os
import sys
import io
import re
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Windows環境での標準出力エンコーディング設定
# Note: Bashツールから実行する場合はコメントアウト
# if sys.platform == 'win32':
#     # bufferが存在し、TextIOWrapperでない場合のみ設定
#     if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
#         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
#     if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
#         sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 環境変数読み込み
load_dotenv()


def generate_slug(title: str = None) -> str:
    """
    スラッグを生成（ファイル名用）

    Args:
        title: 記事のタイトル（省略時はランダム生成）

    Returns:
        str: スラッグ（12～50文字、a-z0-9とハイフン、アンダースコア）

    Note:
        - タイトルからスラッグを生成する場合、英数字以外は削除
        - 12文字未満の場合はタイムスタンプを追加
        - 50文字を超える場合は切り詰め
    """
    if title:
        # タイトルを小文字に変換し、英数字とハイフン、アンダースコア以外を削除
        slug = re.sub(r'[^a-z0-9\-_]', '-', title.lower())
        # 連続するハイフンを1つに
        slug = re.sub(r'-+', '-', slug)
        # 前後のハイフンを削除
        slug = slug.strip('-')
    else:
        slug = ""

    # 12文字未満の場合はタイムスタンプを追加
    if len(slug) < 12:
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        slug = f"{slug}-{timestamp}" if slug else f"article-{timestamp}"

    # 50文字を超える場合は切り詰め
    if len(slug) > 50:
        slug = slug[:50]

    # 最後がハイフンで終わっている場合は削除
    slug = slug.rstrip('-')

    return slug


def create_article_content(
    title: str,
    content: str,
    emoji: str = "📝",
    article_type: str = "tech",
    topics: Optional[List[str]] = None,
    published: bool = True
) -> str:
    """
    Zenn記事のマークダウンコンテンツを生成（フロントマター付き）

    Args:
        title: 記事のタイトル
        content: 記事の本文
        emoji: アイキャッチ絵文字（1文字）
        article_type: 記事タイプ（"tech" or "idea"）
        topics: トピック（タグ）のリスト（最大5個）
        published: 公開設定（True: 公開、False: 下書き）

    Returns:
        str: フロントマター付きマークダウン
    """
    if topics is None:
        topics = []

    # トピックを最大5個に制限
    if len(topics) > 5:
        print(f"⚠️  トピックは最大5個までです。最初の5個のみ使用します: {topics[:5]}")
        topics = topics[:5]

    # 絵文字が1文字かチェック
    if len(emoji) > 1:
        print(f"⚠️  絵文字は1文字のみです。最初の1文字を使用します: {emoji[0]}")
        emoji = emoji[0]

    # topicsをYAML配列形式に変換
    topics_str = '[' + ', '.join([f'"{topic}"' for topic in topics]) + ']'

    frontmatter = f"""---
title: "{title}"
emoji: "{emoji}"
type: "{article_type}"
topics: {topics_str}
published: {str(published).lower()}
---

"""

    return frontmatter + content


def post_to_zenn_github(
    title: str,
    content: str,
    emoji: Optional[str] = "📝",
    article_type: Optional[str] = "tech",
    topics: Optional[List[str]] = None,
    published: bool = True,
    slug: Optional[str] = None,
    dry_run: bool = False
) -> Dict:
    """
    GitHub連携でZennに記事を投稿

    Args:
        title: 記事のタイトル
        content: 記事の本文（マークダウン形式）
        emoji: 記事のアイコン絵文字（デフォルト: 📝）
        article_type: 記事タイプ（"tech" or "idea"、デフォルト: "tech"）
        topics: トピック（タグ）のリスト（最大5個）
        published: Trueの場合、公開記事として投稿（デフォルト: True）
        slug: 記事のスラッグ（省略時は自動生成）
        dry_run: Trueの場合、実際には投稿せずにシミュレーションのみ

    Returns:
        投稿情報の辞書
        {
            'success': bool,
            'file_path': str (成功時のみ),
            'slug': str,
            'title': str,
            'dry_run': bool
        }

    Raises:
        ValueError: 必要な環境変数が設定されていない場合
        Exception: 投稿に失敗した場合
    """
    # トピックのデフォルト値設定
    if topics is None:
        topics = []

    # スラッグを生成（指定がなければ自動生成）
    if not slug:
        slug = generate_slug(title)

    # Dry runモード
    if dry_run:
        print("🔍 [DRY RUN] 実際には投稿しません")
        print(f"  スラッグ: {slug}")
        print(f"  タイトル: {title}")
        print(f"  本文の長さ: {len(content)}文字")
        print(f"  絵文字: {emoji}")
        print(f"  タイプ: {article_type}")
        print(f"  トピック: {', '.join(topics) if topics else 'なし'}")
        print(f"  公開: {'はい' if published else 'いいえ（下書き）'}")
        return {
            'success': True,
            'slug': slug,
            'title': title,
            'content_length': len(content),
            'emoji': emoji,
            'type': article_type,
            'topics': topics,
            'published': published,
            'dry_run': True
        }

    # 環境変数から設定を取得
    repo_path = os.getenv('ZENN_GITHUB_REPO_PATH')

    if not repo_path:
        raise ValueError('ZENN_GITHUB_REPO_PATHを.envに設定してください（Zenn連携Gitリポジトリのパス）')

    repo_path = Path(repo_path)

    # リポジトリパスの存在確認
    if not repo_path.exists():
        raise ValueError(f'指定されたリポジトリパスが存在しません: {repo_path}')

    # articlesディレクトリの確認・作成
    articles_dir = repo_path / 'articles'
    if not articles_dir.exists():
        print(f"📁 articlesディレクトリを作成: {articles_dir}")
        articles_dir.mkdir(parents=True)

    # 記事ファイルのパス
    article_file = articles_dir / f"{slug}.md"

    # ファイルが既に存在する場合は警告
    if article_file.exists():
        print(f"⚠️  既存のファイルを上書きします: {article_file}")

    try:
        # マークダウンコンテンツを生成
        article_content = create_article_content(
            title=title,
            content=content,
            emoji=emoji,
            article_type=article_type,
            topics=topics,
            published=published
        )

        # ファイルに書き込み
        print(f"📝 記事ファイルを作成: {article_file.name}")
        article_file.write_text(article_content, encoding='utf-8')

        # Gitでコミット・プッシュ
        print("🔄 Gitでコミット・プッシュ中...")

        # git add
        result = subprocess.run(
            ['git', 'add', str(article_file)],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode != 0:
            raise Exception(f"git add失敗: {result.stderr}")

        # git commit
        commit_message = f"Add article: {title}"
        result = subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode != 0:
            # コミットするものがない場合はエラーではない
            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                print("⚠️  コミットする変更がありません")
            else:
                raise Exception(f"git commit失敗: {result.stderr}")

        # git push
        print("⬆️  GitHubにプッシュ中...")
        result = subprocess.run(
            ['git', 'push'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode != 0:
            raise Exception(f"git push失敗: {result.stderr}")

        print("✅ GitHubへのプッシュ完了")
        print(f"📄 記事ファイル: {article_file}")
        print("🔄 Zennが自動的に記事を同期します（数分かかる場合があります）")

        return {
            'success': True,
            'file_path': str(article_file),
            'slug': slug,
            'title': title,
            'emoji': emoji,
            'type': article_type,
            'topics': topics,
            'published': published,
            'dry_run': False
        }

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        raise Exception(f"Zenn投稿エラー（GitHub方式）: {e}")


def main():
    """テスト用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='GitHub連携でZennに記事を投稿')
    parser.add_argument('--title', type=str, required=True, help='記事のタイトル')
    parser.add_argument('--content', type=str, help='記事の本文（直接指定）')
    parser.add_argument('--content-file', type=str, help='記事の本文ファイルパス')
    parser.add_argument('--emoji', type=str, default='📝', help='記事の絵文字アイコン')
    parser.add_argument('--type', type=str, default='tech', choices=['tech', 'idea'], help='記事タイプ')
    parser.add_argument('--topics', type=str, nargs='+', help='トピック（タグ）のリスト（スペース区切り、最大5個）')
    parser.add_argument('--draft', action='store_true', help='下書きとして保存（公開しない）')
    parser.add_argument('--slug', type=str, help='記事のスラッグ（省略時は自動生成）')
    parser.add_argument('--dry-run', action='store_true', help='実際には投稿しない')

    args = parser.parse_args()

    # 本文の取得
    if args.content_file:
        content = Path(args.content_file).read_text(encoding='utf-8')
    elif args.content:
        content = args.content
    else:
        parser.error('--content または --content-file のいずれかを指定してください')

    try:
        result = post_to_zenn_github(
            title=args.title,
            content=content,
            emoji=args.emoji,
            article_type=args.type,
            topics=args.topics,
            published=not args.draft,
            slug=args.slug,
            dry_run=args.dry_run
        )

        if result['success']:
            if result['dry_run']:
                print("✅ [DRY RUN] シミュレーション完了")
            else:
                print(f"✅ 投稿成功: {result['file_path']}")
        else:
            print(f"❌ 投稿失敗: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
