#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenn投稿モジュール（GitHub連携方式）のテストスクリプト
"""

from zenn_platform.post_zenn_github import post_to_zenn_github

def test_post_to_zenn_github():
    """GitHub連携方式でZennに記事を投稿（Dry runモード）"""

    # テストデータ
    title = "Pythonで複数プラットフォームへの自動投稿システムを作ってみた"
    content = """# はじめに

技術記事を複数のプラットフォームに投稿するのは手間がかかります。
そこで、Pythonを使って自動投稿システムを作成してみました。

## 使用した技術

- Python 3.x
- Tweepy (X API)
- Selenium (Note.com, Zenn)
- Qiita API v2
- GitHub連携 (Zenn)

## 実装内容

各プラットフォームのAPIやSeleniumを使って、一括投稿を実現しました。

## まとめ

自動化により、記事の投稿作業が大幅に効率化されました。
"""

    emoji = "📝"
    topics = ["Python", "自動化", "API"]

    print("=" * 80)
    print("Zenn GitHub連携投稿テスト")
    print("=" * 80)
    print()

    try:
        # Dry runモードでテスト
        result = post_to_zenn_github(
            title=title,
            content=content,
            emoji=emoji,
            article_type="tech",
            topics=topics,
            published=True,
            dry_run=True  # 実際には投稿しない
        )

        print()
        print("=" * 80)
        print("テスト結果:")
        print("=" * 80)
        print(result)
        print()

        if result['success']:
            print("✅ テスト成功")
            print(f"   スラッグ: {result['slug']}")
            print(f"   タイトル: {result['title']}")
            print(f"   タイプ: {result['type']}")
            print(f"   絵文字: {result['emoji']}")
            print(f"   トピック: {', '.join(result['topics'])}")
        else:
            print("❌ テスト失敗")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False

    return True


if __name__ == '__main__':
    import sys
    success = test_post_to_zenn_github()
    sys.exit(0 if success else 1)
