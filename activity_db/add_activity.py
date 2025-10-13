#!/usr/bin/env python3
"""
Add Activity CLI

活動情報を追加するコマンドラインツール
"""

import sys
import argparse
from datetime import datetime
from db import ActivityDB


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="活動情報をデータベースに追加",
        epilog="例: python add_activity.py \"ClaudeCodeでDB設計完了\""
    )
    parser.add_argument(
        "content",
        help="活動内容"
    )
    parser.add_argument(
        "--timestamp",
        "-t",
        help="タイムスタンプ（ISO8601形式、省略時は現在時刻）"
    )

    args = parser.parse_args()

    try:
        # DB接続
        db = ActivityDB()

        # 活動追加
        print(f"📝 活動を追加しています...")
        print(f"内容: {args.content}")

        activity = db.add_activity(
            content=args.content,
            timestamp=args.timestamp
        )

        # 結果表示
        print("\n" + "=" * 60)
        print("✅ 活動を追加しました")
        print("=" * 60)
        print(f"ID: {activity['id']}")
        print(f"タイムスタンプ: {activity['timestamp']}")
        print(f"内容: {activity['content']}")
        print("=" * 60)

        # 総数表示
        count = db.count_activities()
        print(f"\n📊 総活動数: {count}")

        return 0

    except ValueError as e:
        print(f"❌ 入力エラー: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
