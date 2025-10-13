"""
Activity Database Cleanup Module

古いデータ削除とVACUUM実行
"""

import argparse
from datetime import datetime, timedelta
from typing import Dict
from db import ActivityDB


class ActivityCleanup:
    """活動情報クリーンアップクラス"""

    def __init__(self):
        """初期化"""
        self.db = ActivityDB()

    def delete_old_activities(self, days: int = 90) -> Dict:
        """
        指定日数より古い活動を削除

        Args:
            days: 保持日数（デフォルト: 90日）

        Returns:
            Dict: 削除結果
        """
        try:
            # 削除基準日時を計算
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()

            print(f"🗑️  {days}日以前（{cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}より前）のデータを削除します...")

            # 削除前の件数確認
            before_count = self.db.count_activities()
            print(f"削除前の総件数: {before_count}")

            # 古いデータを削除
            result = self.db.client.table(self.db.table_name)\
                .delete()\
                .lt("timestamp", cutoff_str)\
                .execute()

            deleted_count = len(result.data) if result.data else 0

            # 削除後の件数確認
            after_count = self.db.count_activities()

            result_info = {
                "before_count": before_count,
                "deleted_count": deleted_count,
                "after_count": after_count,
                "cutoff_date": cutoff_str,
                "days": days
            }

            print(f"✅ {deleted_count}件のデータを削除しました")
            print(f"削除後の総件数: {after_count}")

            return result_info

        except Exception as e:
            print(f"❌ データ削除に失敗: {e}")
            raise

    def vacuum_database(self) -> bool:
        """
        VACUUMを実行して容量を解放

        注意: Supabaseの場合、VACUUM は管理者権限が必要なため、
        Supabase Web UIのSQLエディタで以下を実行してください：

        VACUUM FULL activities;

        または定期的な自動VACUUM設定：

        ALTER TABLE activities SET (autovacuum_enabled = true);

        Returns:
            bool: 実行成功時True
        """
        print("\n📦 VACUUM実行について:")
        print("=" * 60)
        print("Supabaseでは、以下の方法でVACUUMを実行できます:")
        print()
        print("1. Web UIのSQL Editorで以下を実行:")
        print("   VACUUM FULL activities;")
        print()
        print("2. または、自動VACUUM を有効化:")
        print("   ALTER TABLE activities SET (autovacuum_enabled = true);")
        print()
        print("3. Supabaseは通常、自動的にVACUUMを実行しますが、")
        print("   大量削除後は手動実行を推奨します。")
        print("=" * 60)

        return True

    def get_database_stats(self) -> Dict:
        """
        データベース統計情報を取得

        Returns:
            Dict: 統計情報
        """
        try:
            total_count = self.db.count_activities()

            # 最古と最新のデータ取得
            oldest = self.db.client.table(self.db.table_name)\
                .select("timestamp")\
                .order("timestamp", desc=False)\
                .limit(1)\
                .execute()

            latest = self.db.client.table(self.db.table_name)\
                .select("timestamp")\
                .order("timestamp", desc=True)\
                .limit(1)\
                .execute()

            stats = {
                "total_count": total_count,
                "oldest_timestamp": oldest.data[0]["timestamp"] if oldest.data else None,
                "latest_timestamp": latest.data[0]["timestamp"] if latest.data else None,
            }

            # 期間計算
            if stats["oldest_timestamp"] and stats["latest_timestamp"]:
                oldest_dt = datetime.fromisoformat(stats["oldest_timestamp"].replace('Z', '+00:00'))
                latest_dt = datetime.fromisoformat(stats["latest_timestamp"].replace('Z', '+00:00'))
                stats["data_period_days"] = (latest_dt - oldest_dt).days

            return stats

        except Exception as e:
            print(f"❌ 統計情報の取得に失敗: {e}")
            raise

    def print_stats(self):
        """統計情報を表示"""
        print("\n📊 データベース統計:")
        print("=" * 60)

        stats = self.get_database_stats()

        print(f"総件数: {stats['total_count']}")

        if stats.get('oldest_timestamp'):
            print(f"最古データ: {stats['oldest_timestamp'][:19]}")

        if stats.get('latest_timestamp'):
            print(f"最新データ: {stats['latest_timestamp'][:19]}")

        if stats.get('data_period_days') is not None:
            print(f"データ期間: {stats['data_period_days']}日")

        print("=" * 60)


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="活動情報データベースのクリーンアップ"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="保持日数（デフォルト: 90日）"
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="統計情報のみ表示（削除は行わない）"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="確認なしで実行"
    )

    args = parser.parse_args()

    cleanup = ActivityCleanup()

    # 統計情報表示
    cleanup.print_stats()

    if args.stats_only:
        print("\n✅ 統計情報のみ表示しました")
        return

    # 削除確認
    if not args.yes:
        print(f"\n⚠️  {args.days}日以前のデータを削除します")
        confirm = input("実行しますか？ (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ キャンセルしました")
            return

    # 古いデータ削除
    result = cleanup.delete_old_activities(days=args.days)

    # VACUUM情報表示
    cleanup.vacuum_database()

    # 削除後の統計表示
    print("\n削除後の統計:")
    cleanup.print_stats()

    print("\n✅ クリーンアップ完了")


if __name__ == "__main__":
    main()
