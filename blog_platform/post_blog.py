#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
静的ブログ生成・デプロイモジュール
マークダウンからHTMLを生成し、FTPでサーバーにアップロード
"""

import os
import sys
import re
import json
import markdown
import ftplib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from jinja2 import Template

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent
BLOG_ROOT = PROJECT_ROOT / 'toshi776-blog'


def parse_frontmatter(content: str) -> tuple[Dict, str]:
    """
    マークダウンファイルのフロントマターをパース

    Args:
        content: マークダウンファイルの内容

    Returns:
        (メタデータ辞書, 本文) のタプル
    """
    # フロントマターの抽出（---で囲まれた部分）
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        # フロントマターがない場合は空の辞書と全文を返す
        return {}, content

    frontmatter_text = match.group(1)
    body = match.group(2)

    # フロントマターをパース
    metadata = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            # タグの配列をパース
            if key == 'tags' and value.startswith('[') and value.endswith(']'):
                tags_str = value[1:-1]  # [] を削除
                metadata[key] = [tag.strip().strip('"').strip("'") for tag in tags_str.split(',')]
            else:
                metadata[key] = value

    return metadata, body


def generate_slug_from_title(title: str, date: str) -> str:
    """
    タイトルと日付からスラッグを生成

    Args:
        title: 記事タイトル
        date: 日付文字列 (YYYY-MM-DD)

    Returns:
        スラッグ (例: "20250110-001")
    """
    date_part = date.replace('-', '')[:8]  # YYYYMMDD
    # 簡易的にカウンターを001とする（実際は既存記事数+1などにする）
    counter = '001'
    return f"{date_part}-{counter}"


def build_post_html(title: str, content: str, metadata: Dict) -> str:
    """
    記事HTMLを生成

    Args:
        title: 記事タイトル
        content: マークダウン本文
        metadata: メタデータ

    Returns:
        生成されたHTML文字列
    """
    # マークダウンをHTMLに変換
    html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])

    # テンプレート読み込み
    template_path = BLOG_ROOT / 'templates' / 'post.html'
    template_content = template_path.read_text(encoding='utf-8')
    template = Template(template_content)

    # 日付フォーマット
    date_str = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%Y/%m/%d')

    # テンプレートに値を埋め込み
    html = template.render(
        title=title,
        description=metadata.get('description', ''),
        datetime=date_str,
        date=formatted_date,
        tags=metadata.get('tags', []),
        content=html_content
    )

    return html


def load_posts_metadata() -> List[Dict]:
    """
    記事メタデータを読み込む

    Returns:
        記事メタデータのリスト
    """
    metadata_file = BLOG_ROOT / 'posts_metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_posts_metadata(posts: List[Dict]):
    """
    記事メタデータを保存

    Args:
        posts: 記事メタデータのリスト
    """
    metadata_file = BLOG_ROOT / 'posts_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


def add_post_to_metadata(slug: str, title: str, metadata: Dict):
    """
    新しい記事をメタデータに追加

    Args:
        slug: 記事のスラッグ
        title: 記事のタイトル
        metadata: 記事のメタデータ
    """
    posts = load_posts_metadata()

    # 既存の記事を更新または新規追加
    existing_post = None
    for post in posts:
        if post['slug'] == slug:
            existing_post = post
            break

    post_data = {
        'slug': slug,
        'title': title,
        'description': metadata.get('description', ''),
        'date': metadata.get('date', datetime.now().strftime('%Y-%m-%d')),
        'datetime': metadata.get('date', datetime.now().strftime('%Y-%m-%d')),
        'tags': metadata.get('tags', [])
    }

    if existing_post:
        # 既存の記事を更新
        posts = [post_data if p['slug'] == slug else p for p in posts]
    else:
        # 新規記事を先頭に追加（最新順）
        posts.insert(0, post_data)

    save_posts_metadata(posts)


def build_index_html() -> str:
    """
    ブログのindex.htmlを生成

    Returns:
        生成されたHTML文字列
    """
    # 記事メタデータを読み込み
    posts = load_posts_metadata()

    # 日付でソート（新しい順）
    posts.sort(key=lambda x: x['datetime'], reverse=True)

    # 日付フォーマットを整形
    for post in posts:
        date_obj = datetime.strptime(post['datetime'], '%Y-%m-%d')
        post['date'] = date_obj.strftime('%Y/%m/%d')

    # テンプレート読み込み
    template_path = BLOG_ROOT / 'templates' / 'index.html'
    template_content = template_path.read_text(encoding='utf-8')
    template = Template(template_content)

    # テンプレートに値を埋め込み
    html = template.render(posts=posts)

    return html


def upload_to_ftp(local_path: Path, remote_path: str, dry_run: bool = False) -> bool:
    """
    FTPでファイルをアップロード

    Args:
        local_path: ローカルファイルパス
        remote_path: リモートファイルパス
        dry_run: Trueの場合、実際にはアップロードしない

    Returns:
        成功したかどうか
    """
    if dry_run:
        print(f"  [DRY RUN] アップロード: {local_path} -> {remote_path}")
        return True

    ftp_host = os.getenv('FTP_HOST')
    ftp_user = os.getenv('FTP_USER')
    ftp_pass = os.getenv('FTP_PASS')

    if not all([ftp_host, ftp_user, ftp_pass]):
        raise ValueError('FTP設定（FTP_HOST, FTP_USER, FTP_PASS）を.envに設定してください')

    try:
        with ftplib.FTP(ftp_host) as ftp:
            ftp.login(ftp_user, ftp_pass)
            ftp.encoding = 'utf-8'

            # ディレクトリ作成（存在しない場合）
            remote_dir = '/'.join(remote_path.split('/')[:-1])
            try:
                ftp.cwd(remote_dir)
            except:
                # ディレクトリが存在しない場合は作成
                dirs = remote_dir.split('/')
                for i in range(len(dirs)):
                    dir_path = '/'.join(dirs[:i+1])
                    try:
                        ftp.cwd(dir_path)
                    except:
                        ftp.mkd(dir_path)
                        ftp.cwd(dir_path)

            # ファイルアップロード
            with open(local_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_path.split("/")[-1]}', file)

        return True

    except Exception as e:
        print(f"  FTPアップロードエラー: {e}")
        return False


def post_to_blog(
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
    description: str = '',
    status: str = 'publish',
    dry_run: bool = False
) -> Dict:
    """
    静的ブログに記事を投稿

    Args:
        title: 記事のタイトル
        content: 記事の本文（マークダウン形式）
        tags: タグのリスト
        description: 記事の説明文
        status: 'publish' or 'draft'
        dry_run: Trueの場合、実際には投稿せずにシミュレーションのみ

    Returns:
        投稿情報の辞書
    """
    if tags is None:
        tags = []

    try:
        # メタデータ作成
        date_str = datetime.now().strftime('%Y-%m-%d')
        metadata = {
            'title': title,
            'date': date_str,
            'description': description or f'{title}に関する記事',
            'tags': tags
        }

        # スラッグ生成
        slug = generate_slug_from_title(title, date_str)

        # Dry runモード
        if dry_run:
            print("🔍 [DRY RUN] 実際には投稿しません")
            print(f"  タイトル: {title}")
            print(f"  本文の長さ: {len(content)}文字")
            print(f"  タグ: {', '.join(tags) if tags else 'なし'}")
            print(f"  スラッグ: {slug}")
            print(f"  ステータス: {status}")
            return {
                'success': True,
                'title': title,
                'slug': slug,
                'url': f'https://toshi776.com/blog/posts/{slug}/',
                'dry_run': True
            }

        # HTML生成
        print(f"📝 HTML生成中...")
        html = build_post_html(title, content, metadata)

        # ビルドディレクトリ作成
        build_dir = BLOG_ROOT / 'build' / 'posts' / slug
        build_dir.mkdir(parents=True, exist_ok=True)

        # HTMLファイル保存
        html_path = build_dir / 'index.html'
        html_path.write_text(html, encoding='utf-8')
        print(f"  ✓ HTML生成完了: {html_path}")

        # 記事メタデータを更新
        print(f"📋 記事一覧を更新中...")
        add_post_to_metadata(slug, title, metadata)

        # index.html生成
        index_html = build_index_html()
        index_path = BLOG_ROOT / 'build' / 'index.html'
        index_path.write_text(index_html, encoding='utf-8')
        print(f"  ✓ index.html生成完了")

        # FTPアップロード
        if status == 'publish':
            print(f"📤 FTPアップロード中...")

            # 記事ページをアップロード
            remote_post_path = f'/public_html/blog/posts/{slug}/index.html'
            if upload_to_ftp(html_path, remote_post_path, dry_run=False):
                print(f"  ✓ 記事ページアップロード完了")
            else:
                raise Exception("記事ページのFTPアップロードに失敗しました")

            # index.htmlをアップロード
            remote_index_path = '/public_html/blog/index.html'
            if upload_to_ftp(index_path, remote_index_path, dry_run=False):
                print(f"  ✓ index.htmlアップロード完了")
            else:
                raise Exception("index.htmlのFTPアップロードに失敗しました")

        article_url = f'https://toshi776.com/blog/posts/{slug}/'

        return {
            'success': True,
            'url': article_url,
            'title': title,
            'slug': slug,
            'status': status,
            'dry_run': False
        }

    except Exception as e:
        raise Exception(f"ブログ投稿エラー: {e}")


def main():
    """テスト用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='静的ブログに記事を投稿')
    parser.add_argument('--title', type=str, required=True, help='記事のタイトル')
    parser.add_argument('--content', type=str, help='記事の本文（直接指定、マークダウン）')
    parser.add_argument('--content-file', type=str, help='記事の本文ファイルパス')
    parser.add_argument('--tags', type=str, nargs='+', help='タグのリスト（スペース区切り）')
    parser.add_argument('--description', type=str, help='記事の説明文')
    parser.add_argument('--status', type=str, default='publish',
                        choices=['publish', 'draft'],
                        help='投稿ステータス（デフォルト: publish）')
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
        result = post_to_blog(
            title=args.title,
            content=content,
            tags=args.tags,
            description=args.description or '',
            status=args.status,
            dry_run=args.dry_run
        )

        if result['success']:
            if result['dry_run']:
                print("✅ [DRY RUN] シミュレーション完了")
            else:
                print(f"✅ 投稿成功: {result['url']}")
        else:
            print(f"❌ 投稿失敗: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
