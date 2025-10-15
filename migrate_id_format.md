# Activity ID フォーマット変更手順

## 変更内容
- **変更前**: UUID形式（例: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`）
- **変更後**: 5桁数字形式（例: `00001`, `00002`, ...）
- **対応範囲**: 最大99,999件まで対応可能

## 手順

### 1. Supabase Web UIでのテーブル変更

Supabase Web UI > SQL Editorで以下のSQLを順番に実行してください。

#### Step 1: 新しいテーブル作成

```sql
-- 新しいフォーマットのテーブルを作成
CREATE TABLE activities_new (
    id VARCHAR(5) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_activities_new_timestamp ON activities_new(timestamp DESC);
```

#### Step 2: 既存データを新IDで移行

```sql
-- 既存データを timestamp 順に取得し、00001 から採番して挿入
INSERT INTO activities_new (id, timestamp, content, created_at)
SELECT
    LPAD(ROW_NUMBER() OVER (ORDER BY timestamp ASC)::TEXT, 5, '0') as id,
    timestamp,
    content,
    created_at
FROM activities
ORDER BY timestamp ASC;
```

#### Step 3: データ確認

```sql
-- 移行されたデータを確認
SELECT * FROM activities_new ORDER BY id ASC LIMIT 10;

-- 件数確認
SELECT COUNT(*) FROM activities;
SELECT COUNT(*) FROM activities_new;
```

#### Step 4: テーブルの入れ替え（データ確認後に実行）

```sql
-- 古いテーブルをバックアップとして残す
ALTER TABLE activities RENAME TO activities_old;

-- 新しいテーブルを本番テーブル名に変更
ALTER TABLE activities_new RENAME TO activities;
```

#### Step 5: 古いテーブルの削除（任意、確認後に実行）

```sql
-- 問題がなければ古いテーブルを削除
-- ※この操作は取り消せないので注意
DROP TABLE activities_old;
```

### 2. アプリケーションコードの変更

`activity_db/db.py` のコメントとドキュメントを更新：

```python
def init_table(self) -> bool:
    """
    テーブル初期化（初回のみ実行）

    注意: SupabaseのWeb UIまたはSQLエディタで以下を実行してください：

    CREATE TABLE activities (
        id VARCHAR(5) PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE INDEX idx_activities_timestamp ON activities(timestamp DESC);

    Returns:
        bool: テーブルが存在する場合True
    """
```

### 3. 新規データの採番機能追加

新しいデータを追加する際、自動で連番を振る機能を追加：

```python
def _get_next_id(self) -> str:
    """
    次のIDを取得（5桁の連番）

    Returns:
        str: 次のID（例: '00001'）
    """
    try:
        # 最大IDを取得
        result = self.client.table(self.table_name)\
            .select("id")\
            .order("id", desc=True)\
            .limit(1)\
            .execute()

        if result.data and len(result.data) > 0:
            max_id = int(result.data[0]['id'])
            next_id = max_id + 1
        else:
            next_id = 1

        return str(next_id).zfill(5)

    except Exception as e:
        print(f"❌ 次のIDの取得に失敗: {e}")
        raise

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

    # 次のIDを取得
    next_id = self._get_next_id()

    data = {
        "id": next_id,
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
```

## 注意事項

1. **バックアップ**: 必ず `activities_old` テーブルを残して動作確認してから削除してください
2. **ID採番**: 既存データは `timestamp` の昇順で `00001` から採番されます
3. **新規データ**: 今後追加されるデータは自動で連番が振られます
4. **並行実行**: ID採番時に競合が発生する可能性があるため、本番環境では注意が必要です

## ロールバック方法

問題が発生した場合：

```sql
-- 新しいテーブルを削除
DROP TABLE activities;

-- 古いテーブルを復元
ALTER TABLE activities_old RENAME TO activities;
```
