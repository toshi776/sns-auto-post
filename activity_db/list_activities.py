#!/usr/bin/env python3
"""
List Activities CLI

活動情報一覧を表示するコマンドラインツール
"""

import sys
import argparse
from db import ActivityDB


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="活動情報一覧を表示"
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="表示件数（デフォルト: 10）"
    )
    parser.add_argument(
        "--offset",
        "-o",
        type=int,
        default=0,
        help="オフセット（デフォルト: 0）"
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="最新の1件のみ表示"
    )

    args = parser.parse_args()

    try:
        # DB接続
        db = ActivityDB()

        # 総数取得
        total_count = db.count_activities()

        if args.latest:
            # 最新1件のみ表示
            print("🔍 最新の活動を取得中...")
            activity = db.get_latest()

            if not activity:
                print("⚠️ 活動情報が見つかりませんでした")
                return 0

            print("\n" + "=" * 60)
            print("📝 最新の活動")
            print("=" * 60)
            print(f"ID: {activity['id']}")
            print(f"タイムスタンプ: {activity['timestamp']}")
            print(f"内容:\n{activity['content']}")
            print("=" * 60)

        else:
            # 一覧表示
            print(f"🔍 活動一覧を取得中... (総数: {total_count})")

            activities = db.list_activities(
                limit=args.limit,
                offset=args.offset
            )

            if not activities:
                print("⚠️ 活動情報が見つかりませんでした")
                return 0

            print("\n" + "=" * 60)
            print(f"📋 活動一覧 ({args.offset + 1} ~ {args.offset + len(activities)} / {total_count})")
            print("=" * 60)

            for i, activity in enumerate(activities, start=args.offset + 1):
                timestamp = activity['timestamp'][:19]  # 秒まで表示
                content_preview = activity['content'][:60]
                if len(activity['content']) > 60:
                    content_preview += "..."

                print(f"\n{i}. [{timestamp}]")
                print(f"   ID: {activity['id']}")
                print(f"   {content_preview}")

            print("\n" + "=" * 60)

        return 0

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
