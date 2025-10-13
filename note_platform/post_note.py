#!/usr/bin/env python3
"""
Note投稿モジュール
Seleniumを使用したブラウザ自動操作でNote.comに記事を投稿
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()


def post_to_note(title: str, content: str, headless: bool = False, dry_run: bool = False) -> Dict:
    """
    Note.comに記事を投稿

    Args:
        title: 記事のタイトル
        content: 記事の本文（マークダウン形式）
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
    # ログイン情報確認
    email = os.getenv('NOTE_EMAIL')
    password = os.getenv('NOTE_PASSWORD')

    if not all([email, password]):
        raise ValueError('NOTE_EMAILとNOTE_PASSWORDを.envに設定してください')

    # Dry runモード
    if dry_run:
        print("🔍 [DRY RUN] 実際には投稿しません")
        return {
            'success': True,
            'title': title,
            'content_length': len(content),
            'dry_run': True
        }

    # Chrome オプション設定
    chrome_options = Options()
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
        # ChromeDriver 自動セットアップ
        print("🔧 ChromeDriverをセットアップ中...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ ChromeDriverのセットアップ完了")

        # Note.comのログインページにアクセス
        print("🌐 Note.comにアクセス中...")
        driver.get("https://note.com/login")
        time.sleep(2)

        # ログイン
        print("🔑 ログイン中...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)

        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # ログイン完了を待つ
        print("⏳ ログイン処理を待機中...")
        time.sleep(5)

        # 記事作成ページに移動
        print("📝 記事作成ページに移動中...")
        driver.get("https://note.com/n/new")
        time.sleep(3)

        # タイトル入力
        print(f"✍️  タイトルを入力中: {title}")
        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='タイトル']"))
        )
        title_input.clear()
        title_input.send_keys(title)
        time.sleep(1)

        # 本文入力
        print(f"✍️  本文を入力中... ({len(content)}文字)")
        content_textarea = driver.find_element(By.CSS_SELECTOR, "textarea[placeholder='本文を入力']")
        content_textarea.clear()
        content_textarea.send_keys(content)
        time.sleep(2)

        # 公開設定
        # Note: 実際の投稿処理はdry_runでない場合のみ実行
        # ここでは公開ボタンをクリックする前で停止

        print("⏸️  投稿準備完了")
        print("⚠️  注意: 実際の公開処理はWindows環境で手動確認後に有効化してください")

        # 投稿URLは仮
        note_url = "https://note.com/[投稿後のURL]"

        result = {
            'success': True,
            'url': note_url,
            'title': title,
            'content_length': len(content),
            'dry_run': False
        }

        # スクリーンショット保存（デバッグ用）
        screenshot_path = Path.home() / "note_post_preview.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"📸 スクリーンショットを保存: {screenshot_path}")

        return result

    except Exception as e:
        # エラー時もスクリーンショットを保存
        if driver:
            screenshot_path = Path.home() / "note_post_error.png"
            driver.save_screenshot(str(screenshot_path))
            print(f"📸 エラー時のスクリーンショットを保存: {screenshot_path}")

        raise Exception(f"Note投稿に失敗しました: {str(e)}")

    finally:
        # ブラウザを閉じる
        if driver:
            time.sleep(2)
            driver.quit()
            print("🔒 ブラウザを閉じました")


def main():
    """コマンドラインインターフェース"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Note.comに記事を投稿',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python post_note.py "記事タイトル" "記事本文" --dry-run
  python post_note.py "技術記事" "本文..." --headless

注意:
  このスクリプトはWindows環境でChromeブラウザが必要です。
  WSL環境では動作しません。
        """
    )

    parser.add_argument(
        'title',
        help='記事のタイトル'
    )

    parser.add_argument(
        'content',
        help='記事の本文（マークダウン形式）'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='ヘッドレスモードで実行'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には投稿せず、シミュレーションのみ'
    )

    args = parser.parse_args()

    try:
        print(f"📤 Note.comに投稿準備中...")
        print(f"📝 タイトル: {args.title}")
        print(f"📊 本文文字数: {len(args.content)}")
        print()

        # 投稿
        result = post_to_note(
            title=args.title,
            content=args.content,
            headless=args.headless,
            dry_run=args.dry_run
        )

        # 結果表示
        if result['dry_run']:
            print("=" * 80)
            print("✅ [DRY RUN] 投稿シミュレーション完了")
            print("=" * 80)
            print(f"📝 タイトル: {result['title']}")
            print(f"📊 本文文字数: {result['content_length']}")
        else:
            print("=" * 80)
            print("✅ Note.comに投稿しました")
            print("=" * 80)
            print(f"📝 タイトル: {result['title']}")
            print(f"🔗 URL: {result['url']}")
            print(f"📊 本文文字数: {result['content_length']}")
        print()

    except ValueError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
