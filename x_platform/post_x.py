#!/usr/bin/env python3
"""
X投稿モジュール
Twitter APIを使用してXに投稿
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import tweepy

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()


def post_to_x(text: str, dry_run: bool = False) -> dict:
    """
    Xに投稿

    Args:
        text: 投稿する文章
        dry_run: Trueの場合、実際には投稿せずにシミュレーションのみ

    Returns:
        投稿情報の辞書
        {
            'success': bool,
            'tweet_id': str (成功時のみ),
            'url': str (成功時のみ),
            'text': str,
            'dry_run': bool
        }

    Raises:
        ValueError: APIキーが設定されていない場合
        Exception: 投稿に失敗した場合
    """
    # APIキー確認
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError('X API認証情報を.envに設定してください（X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET）')

    # Dry runモード
    if dry_run:
        print("🔍 [DRY RUN] 実際には投稿しません")
        return {
            'success': True,
            'text': text,
            'dry_run': True
        }

    try:
        # Twitter API v2クライアント作成
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # 投稿
        response = client.create_tweet(text=text)

        # 投稿ID取得
        tweet_id = response.data['id']

        # ユーザー名を取得（URL生成のため）
        # Note: v2 APIではユーザー情報を別途取得する必要がある
        me = client.get_me()
        username = me.data.username

        tweet_url = f"https://x.com/{username}/status/{tweet_id}"

        return {
            'success': True,
            'tweet_id': tweet_id,
            'url': tweet_url,
            'text': text,
            'dry_run': False
        }

    except tweepy.TweepyException as e:
        raise Exception(f"X投稿に失敗しました: {str(e)}")
    except Exception as e:
        raise Exception(f"予期しないエラー: {str(e)}")


def main():
    """コマンドラインインターフェース"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Xに投稿',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python post_x.py "こんにちは、Xの世界！"
  python post_x.py "テスト投稿" --dry-run
        """
    )

    parser.add_argument(
        'text',
        help='投稿する文章'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には投稿せず、シミュレーションのみ'
    )

    args = parser.parse_args()

    try:
        print(f"📤 Xに投稿中...")
        print(f"📝 投稿内容:")
        print("-" * 60)
        print(args.text)
        print("-" * 60)
        print()

        # 投稿
        result = post_to_x(args.text, dry_run=args.dry_run)

        # 結果表示
        if result['dry_run']:
            print("=" * 60)
            print("✅ [DRY RUN] 投稿シミュレーション完了")
            print("=" * 60)
            print(f"📊 文字数: {len(result['text'])}")
        else:
            print("=" * 60)
            print("✅ Xに投稿しました")
            print("=" * 60)
            print(f"🆔 Tweet ID: {result['tweet_id']}")
            print(f"🔗 URL: {result['url']}")
            print(f"📊 文字数: {len(result['text'])}")
        print()

    except ValueError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
