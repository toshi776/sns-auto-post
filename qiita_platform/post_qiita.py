#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qiita投稿モジュール
Qiita API v2を使用して記事を投稿
"""

import os
import sys
import io
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Windows環境での標準出力エンコーディング設定
# Note: Bashツールから実行する場合はコメントアウト
# if sys.platform == 'win32':
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
#     sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()


def post_to_qiita(
    title: str,
    content: str,
    tags: Optional[List[str]] = None,
    private: bool = False,
    tweet: bool = False,
    dry_run: bool = False
) -> Dict:
    """
    Qiitaに記事を投稿

    Args:
        title: 記事のタイトル
        content: 記事の本文（マークダウン形式）
        tags: タグのリスト（例: ["Python", "API"]）。デフォルトは空リスト
        private: Trueの場合、限定共有記事として投稿（デフォルト: False）
        tweet: Trueの場合、Twitter連携で投稿（デフォルト: False）
        dry_run: Trueの場合、実際には投稿せずにシミュレーションのみ

    Returns:
        投稿情報の辞書
        {
            'success': bool,
            'url': str (成功時のみ),
            'title': str,
            'dry_run': bool,
            'error': str (失敗時のみ)
        }

    Raises:
        ValueError: APIトークンが設定されていない場合
        Exception: 投稿に失敗した場合
    """
    # タグのデフォルト値設定
    if tags is None:
        tags = []

    # Dry runモード
    if dry_run:
        print("🔍 [DRY RUN] 実際には投稿しません")
        print(f"  タイトル: {title}")
        print(f"  本文の長さ: {len(content)}文字")
        print(f"  タグ: {', '.join(tags) if tags else 'なし'}")
        print(f"  限定共有: {'はい' if private else 'いいえ'}")
        print(f"  Twitter連携: {'はい' if tweet else 'いいえ'}")
        return {
            'success': True,
            'title': title,
            'content_length': len(content),
            'tags': tags,
            'private': private,
            'dry_run': True
        }

    # APIトークン確認（実際に投稿する場合のみ）
    api_token = os.getenv('QIITA_ACCESS_TOKEN')

    if not api_token:
        raise ValueError('QIITA_ACCESS_TOKENを.envに設定してください')

    # Qiita API v2エンドポイント
    url = 'https://qiita.com/api/v2/items'

    # リクエストヘッダー
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    # リクエストボディ
    # タグの形式: [{"name": "Python", "versions": []}, ...]
    tags_formatted = [{"name": tag, "versions": []} for tag in tags]

    payload = {
        'title': title,
        'body': content,
        'tags': tags_formatted,
        'private': private,
        'tweet': tweet
    }

    try:
        # API呼び出し
        print(f"📤 Qiita APIに投稿中...")
        print(f"  タイトル: {title}")
        print(f"  本文の長さ: {len(content)}文字")
        print(f"  タグ: {', '.join(tags) if tags else 'なし'}")
        print(f"  限定共有: {'はい' if private else 'いいえ'}")

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        # ステータスコード確認
        if response.status_code == 201:
            # 成功（201 Created）
            result = response.json()
            article_url = result.get('url', '')

            return {
                'success': True,
                'url': article_url,
                'title': title,
                'id': result.get('id'),
                'dry_run': False
            }
        else:
            # エラー処理
            error_msg = f"API Error (Status {response.status_code})"
            try:
                error_detail = response.json()
                if 'message' in error_detail:
                    error_msg += f": {error_detail['message']}"
                elif 'error' in error_detail:
                    error_msg += f": {error_detail['error']}"
            except:
                error_msg += f": {response.text}"

            raise Exception(error_msg)

    except requests.exceptions.Timeout:
        raise Exception("APIリクエストがタイムアウトしました")
    except requests.exceptions.ConnectionError:
        raise Exception("ネットワーク接続エラーが発生しました")
    except requests.exceptions.RequestException as e:
        raise Exception(f"APIリクエストエラー: {e}")
    except Exception as e:
        raise Exception(f"Qiita投稿エラー: {e}")


def main():
    """テスト用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='Qiitaに記事を投稿')
    parser.add_argument('--title', type=str, required=True, help='記事のタイトル')
    parser.add_argument('--content', type=str, help='記事の本文（直接指定）')
    parser.add_argument('--content-file', type=str, help='記事の本文ファイルパス')
    parser.add_argument('--tags', type=str, nargs='+', help='タグのリスト（スペース区切り）')
    parser.add_argument('--private', action='store_true', help='限定共有記事として投稿')
    parser.add_argument('--tweet', action='store_true', help='Twitter連携で投稿')
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
        result = post_to_qiita(
            title=args.title,
            content=content,
            tags=args.tags,
            private=args.private,
            tweet=args.tweet,
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
