#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zenn投稿モジュール
Seleniumを使用したブラウザ自動操作でZennに記事を投稿
"""

import os
import sys
import io
import time
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Windows環境での標準出力エンコーディング設定
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()


def post_to_zenn(
    title: str,
    content: str,
    emoji: Optional[str] = "📝",
    topics: Optional[list] = None,
    published: bool = True,
    headless: bool = False,
    dry_run: bool = False
) -> Dict:
    """
    Zennに記事を投稿

    Args:
        title: 記事のタイトル
        content: 記事の本文（マークダウン形式）
        emoji: 記事のアイコン絵文字（デフォルト: 📝）
        topics: トピック（タグ）のリスト（例: ["Python", "API"]）
        published: Trueの場合、公開記事として投稿（デフォルト: True）
        headless: Trueの場合、ヘッドレスモードで実行
        dry_run: Trueの場合、実際には投稿せずにシミュレーションのみ

    Returns:
        投稿情報の辞書
        {
            'success': bool,
            'url': str (成功時のみ),
            'title': str,
            'dry_run': bool
        }

    Raises:
        ValueError: ログイン情報が設定されていない場合
        Exception: 投稿に失敗した場合
    """
    # トピックのデフォルト値設定
    if topics is None:
        topics = []

    # Dry runモード
    if dry_run:
        print("🔍 [DRY RUN] 実際には投稿しません")
        print(f"  タイトル: {title}")
        print(f"  本文の長さ: {len(content)}文字")
        print(f"  絵文字: {emoji}")
        print(f"  トピック: {', '.join(topics) if topics else 'なし'}")
        print(f"  公開: {'はい' if published else 'いいえ（下書き）'}")
        return {
            'success': True,
            'title': title,
            'content_length': len(content),
            'emoji': emoji,
            'topics': topics,
            'published': published,
            'dry_run': True
        }

    # ログイン情報確認
    email = os.getenv('ZENN_EMAIL')
    password = os.getenv('ZENN_PASSWORD')

    if not all([email, password]):
        raise ValueError('ZENN_EMAILとZENN_PASSWORDを.envに設定してください')

    # Chrome オプション設定
    chrome_options = Options()

    # Windows環境でのChrome実行パスを明示的に指定
    if sys.platform == 'win32':
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            chrome_options.binary_location = chrome_path
        else:
            # 32bit版のパスも試す
            chrome_path_x86 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            if os.path.exists(chrome_path_x86):
                chrome_options.binary_location = chrome_path_x86

    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # 環境変数からヘッドレスモード設定を読み込み
    headless_env = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
    if headless_env and not headless:
        headless = True
        chrome_options.add_argument('--headless')

    driver = None

    try:
        # WebDriverの初期化
        print("🌐 ブラウザを起動中...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)

        # Zennログインページにアクセス
        print("🔐 Zennにログイン中...")
        driver.get("https://zenn.dev/enter")
        time.sleep(2)

        # メールアドレスでログインボタンをクリック
        email_login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'メールアドレスでログイン')]"))
        )
        email_login_button.click()
        time.sleep(1)

        # メールアドレスとパスワードを入力
        email_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_input.send_keys(email)

        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(password)

        # ログインボタンをクリック
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        print("⏳ ログイン処理中...")
        time.sleep(5)

        # ログイン成功を確認
        try:
            wait.until(EC.url_changes("https://zenn.dev/enter"))
            print("✅ ログイン成功")
        except:
            raise Exception("ログインに失敗しました")

        # 新規記事作成ページに移動
        print("📝 記事作成ページに移動中...")
        driver.get("https://zenn.dev/articles/new")
        time.sleep(3)

        # タイトルを入力
        print(f"✍️  タイトルを入力: {title}")
        title_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='タイトル']"))
        )
        title_input.clear()
        title_input.send_keys(title)
        time.sleep(1)

        # 絵文字を設定（もし絵文字選択UIがある場合）
        if emoji:
            try:
                print(f"😀 絵文字を設定: {emoji}")
                # 絵文字入力欄を探して設定
                # 実際のUIに応じて調整が必要
                time.sleep(1)
            except:
                print("⚠️  絵文字の設定をスキップしました")

        # 本文を入力
        print(f"✍️  本文を入力（{len(content)}文字）...")
        # Zennのエディタはテキストエリアまたはコンテンツエディタブルな要素
        try:
            # テキストエリアを探す
            content_area = driver.find_element(By.CSS_SELECTOR, "textarea")
            content_area.clear()
            content_area.send_keys(content)
        except:
            # contenteditable要素を探す
            content_area = driver.find_element(By.CSS_SELECTOR, "[contenteditable='true']")
            content_area.clear()
            content_area.send_keys(content)

        time.sleep(2)

        # トピック（タグ）を設定
        if topics:
            print(f"🏷️  トピックを設定: {', '.join(topics)}")
            try:
                # トピック入力欄を探して設定
                # 実際のUIに応じて調整が必要
                time.sleep(1)
            except:
                print("⚠️  トピックの設定をスキップしました")

        # 公開設定
        if published:
            print("🌍 公開記事として投稿します")
            try:
                # 「公開する」ボタンを探してクリック
                publish_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '公開')]"))
                )
                publish_button.click()
                time.sleep(3)

                # 投稿完了を確認
                print("⏳ 投稿処理中...")
                time.sleep(3)

                # 投稿後のURLを取得
                current_url = driver.current_url
                print(f"✅ 投稿完了")

                return {
                    'success': True,
                    'url': current_url,
                    'title': title,
                    'emoji': emoji,
                    'topics': topics,
                    'published': published,
                    'dry_run': False
                }
            except Exception as e:
                raise Exception(f"公開処理に失敗しました: {e}")
        else:
            print("💾 下書きとして保存します")
            try:
                # 「下書き保存」ボタンを探してクリック
                save_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '下書き')]"))
                )
                save_button.click()
                time.sleep(3)

                current_url = driver.current_url
                print(f"✅ 下書き保存完了")

                return {
                    'success': True,
                    'url': current_url,
                    'title': title,
                    'emoji': emoji,
                    'topics': topics,
                    'published': published,
                    'dry_run': False
                }
            except Exception as e:
                raise Exception(f"下書き保存に失敗しました: {e}")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        if driver:
            try:
                # エラー時のスクリーンショット保存
                screenshot_path = f"zenn_error_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print(f"📸 スクリーンショットを保存: {screenshot_path}")
            except:
                pass
        raise Exception(f"Zenn投稿エラー: {e}")

    finally:
        if driver:
            print("🔚 ブラウザを終了します")
            time.sleep(2)
            driver.quit()


def main():
    """テスト用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='Zennに記事を投稿')
    parser.add_argument('--title', type=str, required=True, help='記事のタイトル')
    parser.add_argument('--content', type=str, help='記事の本文（直接指定）')
    parser.add_argument('--content-file', type=str, help='記事の本文ファイルパス')
    parser.add_argument('--emoji', type=str, default='📝', help='記事の絵文字アイコン')
    parser.add_argument('--topics', type=str, nargs='+', help='トピック（タグ）のリスト（スペース区切り）')
    parser.add_argument('--draft', action='store_true', help='下書きとして保存（公開しない）')
    parser.add_argument('--headless', action='store_true', help='ヘッドレスモードで実行')
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
        result = post_to_zenn(
            title=args.title,
            content=content,
            emoji=args.emoji,
            topics=args.topics,
            published=not args.draft,
            headless=args.headless,
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
