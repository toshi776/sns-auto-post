"""
Activity Database Core Module

Supabase接続と活動情報のCRUD操作を提供
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# 環境変数読み込み
load_dotenv()


class ActivityDB:
    """活動情報データベース操作クラス"""

    def __init__(self):
        """Supabase接続初期化"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URLとSUPABASE_KEYを.envに設定してください"
            )

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.table_name = "activities"

    def init_table(self) -> bool:
        """
        テーブル初期化（初回のみ実行）

        注意: SupabaseのWeb UIまたはSQLエディタで以下を実行してください：

        CREATE TABLE activities (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX idx_activities_timestamp ON activities(timestamp DESC);

        Returns:
            bool: テーブルが存在する場合True
        """
        try:
            # テーブル存在確認（1件取得を試みる）
            result = self.client.table(self.table_name).select("id").limit(1).execute()
            print(f"✅ テーブル '{self.table_name}' は既に存在します")
            return True
        except Exception as e:
            print(f"❌ テーブルが存在しません: {e}")
            print("\nSupabase Web UIで以下のSQLを実行してください:")
            print("""
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_activities_timestamp ON activities(timestamp DESC);
            """)
            return False

    def add_activity(self, content: str, timestamp: Optional[str] = None) -> Dict:
        """
        活動情報を追加

        Args:
            content: 活動内容
            timestamp: タイムスタンプ（ISO8601形式）省略時は現在時刻

        Returns:
            Dict: 追加された活動情報
        """
        if not content or not content.strip():
            raise ValueError("活動内容は必須です")

        data = {
            "content": content.strip(),
        }

        if timestamp:
            data["timestamp"] = timestamp

        try:
            result = self.client.table(self.table_name).insert(data).execute()

            if result.data and len(result.data) > 0:
                activity = result.data[0]
                print(f"✅ 活動を追加しました: ID={activity['id']}")
                return activity
            else:
                raise Exception("データの追加に失敗しました")

        except Exception as e:
            print(f"❌ 活動の追加に失敗: {e}")
            raise

    def get_activity(self, activity_id: str) -> Optional[Dict]:
        """
        ID指定で活動情報を取得

        Args:
            activity_id: 活動ID（UUID）

        Returns:
            Optional[Dict]: 活動情報、存在しない場合None
        """
        try:
            result = self.client.table(self.table_name)\
                .select("*")\
                .eq("id", activity_id)\
                .execute()

            if result.data and len(result.data) > 0:
                return result.data[0]
            else:
                print(f"⚠️ ID={activity_id} の活動は見つかりませんでした")
                return None

        except Exception as e:
            print(f"❌ 活動の取得に失敗: {e}")
            raise

    def get_latest(self, limit: int = 1) -> Optional[Dict]:
        """
        最新の活動情報を取得

        Args:
            limit: 取得件数（デフォルト: 1）

        Returns:
            Optional[Dict]: 最新の活動情報、存在しない場合None
        """
        try:
            result = self.client.table(self.table_name)\
                .select("*")\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .execute()

            if result.data and len(result.data) > 0:
                if limit == 1:
                    return result.data[0]
                else:
                    return result.data
            else:
                print("⚠️ 活動情報が見つかりませんでした")
                return None

        except Exception as e:
            print(f"❌ 最新活動の取得に失敗: {e}")
            raise

    def list_activities(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        活動情報一覧を取得

        Args:
            limit: 取得件数（デフォルト: 10）
            offset: オフセット（デフォルト: 0）

        Returns:
            List[Dict]: 活動情報のリスト
        """
        try:
            result = self.client.table(self.table_name)\
                .select("*")\
                .order("timestamp", desc=True)\
                .limit(limit)\
                .range(offset, offset + limit - 1)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            print(f"❌ 活動一覧の取得に失敗: {e}")
            raise

    def count_activities(self) -> int:
        """
        活動情報の総数を取得

        Returns:
            int: 活動情報の総数
        """
        try:
            result = self.client.table(self.table_name)\
                .select("id", count="exact")\
                .execute()

            return result.count if result.count is not None else 0

        except Exception as e:
            print(f"❌ 活動数の取得に失敗: {e}")
            raise


# モジュールレベルの便利関数
def get_db() -> ActivityDB:
    """ActivityDBインスタンスを取得"""
    return ActivityDB()


if __name__ == "__main__":
    # テスト実行
    print("=== Activity DB Test ===")

    db = ActivityDB()

    # テーブル初期化確認
    print("\n1. テーブル確認:")
    db.init_table()

    # 活動追加テスト
    print("\n2. 活動追加テスト:")
    activity = db.add_activity("テスト活動: DB接続確認")
    print(f"追加された活動: {activity}")

    # 最新取得テスト
    print("\n3. 最新活動取得テスト:")
    latest = db.get_latest()
    print(f"最新活動: {latest}")

    # 一覧取得テスト
    print("\n4. 活動一覧取得テスト:")
    activities = db.list_activities(limit=5)
    print(f"活動数: {len(activities)}")
    for i, act in enumerate(activities, 1):
        print(f"  {i}. [{act['timestamp'][:19]}] {act['content'][:50]}...")

    # 総数取得テスト
    print("\n5. 総数取得テスト:")
    count = db.count_activities()
    print(f"総活動数: {count}")

    print("\n✅ テスト完了")
