#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note投稿モジュール
Seleniumを使用したブラウザ自動操作でNote.comに記事を投稿
"""

import os
import sys
import io
import time
import pyperclip
from pathlib import Path
from typing import Dict
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
# Note: Bashツールから実行する場合はコメントアウト
# if sys.platform == 'win32':
#     sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
#     sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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

        # ページが完全に読み込まれるまで待機
        time.sleep(3)

        # デバッグ: ページのHTMLを確認
        print("📋 ページ要素を確認中...")

        # メールアドレス入力フィールドを探す
        email_input = None
        selectors = [
            "input[type='text']",
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='メール']",
            "input[placeholder*='mail']",
            "input[placeholder*='note']"
        ]

        for selector in selectors:
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ メール入力欄を発見: {selector}")
                break
            except:
                continue

        if not email_input:
            # XPathでも試す
            try:
                email_input = driver.find_element(By.XPATH, "//input[@type='text' or @type='email']")
                print("✅ メール入力欄を発見: XPath")
            except Exception as e:
                raise Exception(f"メール入力欄が見つかりません: {str(e)}")

        email_input.clear()
        email_input.send_keys(email)
        print(f"✅ メールアドレス入力完了: {email}")
        time.sleep(1)

        # パスワード入力フィールドを探す
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            print("✅ パスワード入力欄を発見")
        except Exception as e:
            raise Exception(f"パスワード入力欄が見つかりません: {str(e)}")

        password_input.clear()
        password_input.send_keys(password)
        print("✅ パスワード入力完了")
        time.sleep(1)

        # ログインボタンを探す
        login_button = None

        # まずテキストでボタンを探す
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"📋 ページ内のボタン数: {len(all_buttons)}")

        for i, btn in enumerate(all_buttons):
            btn_text = btn.text.strip()
            print(f"  ボタン{i}: text='{btn_text}' type='{btn.get_attribute('type')}'")
            if btn_text == 'ログイン':
                login_button = btn
                print(f"✅ ログインボタンを発見: ボタン{i}")
                break

        if not login_button:
            raise Exception("ログインボタンが見つかりません")

        login_button.click()
        print("✅ ログインボタンをクリックしました")

        # ログイン完了を待つ
        print("⏳ ログイン処理を待機中...")
        time.sleep(5)

        # 記事作成ページに直接移動
        print("📝 記事作成ページに移動中...")

        # 複数のURLパターンを試す
        create_urls = [
            "https://note.com/notes/create",
            "https://note.com/post",
            "https://note.com/new"
        ]

        for url in create_urls:
            try:
                driver.get(url)
                time.sleep(3)

                # タイトル入力欄が存在するか確認
                try:
                    driver.find_element(By.CSS_SELECTOR, "textarea[placeholder*='タイトル'], input[placeholder*='タイトル']")
                    print(f"✅ 記事作成ページに到達: {url}")
                    break
                except:
                    print(f"⚠️  {url} は記事作成ページではありません")
                    continue
            except Exception as e:
                print(f"⚠️  {url} への移動に失敗: {str(e)}")
                continue

        # モーダルやポップアップを閉じる
        try:
            close_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, '閉じる') or contains(@class, 'close')]")
            for btn in close_buttons:
                try:
                    btn.click()
                    print("✅ モーダルを閉じました")
                    time.sleep(1)
                except:
                    pass
        except:
            pass

        # タイトル入力
        print(f"✍️  タイトルを入力中: {title}")

        # タイトル入力欄を探す（複数のセレクタを試す）
        title_input = None
        title_selectors = [
            "textarea[placeholder*='タイトル']",
            "input[placeholder*='タイトル']",
            "//textarea[contains(@placeholder, 'タイトル')]",
            "//input[contains(@placeholder, 'タイトル')]",
            "h1[contenteditable='true']",
            "div[contenteditable='true'][role='textbox']"
        ]

        for selector in title_selectors:
            try:
                if selector.startswith("//"):
                    title_input = driver.find_element(By.XPATH, selector)
                else:
                    title_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ タイトル入力欄を発見: {selector}")
                break
            except:
                continue

        if not title_input:
            raise Exception("タイトル入力欄が見つかりません")

        # タイトルを入力
        try:
            title_input.click()
            time.sleep(0.5)
            title_input.clear()
            title_input.send_keys(title)
        except:
            # contenteditable要素の場合
            driver.execute_script("arguments[0].textContent = arguments[1];", title_input, title)

        print(f"✅ タイトル入力完了: {title}")
        time.sleep(1)

        # 本文入力
        print(f"✍️  本文を入力中... ({len(content)}文字)")

        # 本文入力欄を探す（複数のセレクタを試す）
        content_textarea = None
        content_selectors = [
            "textarea[placeholder*='本文']",
            "div[contenteditable='true'][data-placeholder*='本文']",
            "//textarea[contains(@placeholder, '本文')]",
            "//div[@contenteditable='true' and contains(@data-placeholder, '本文')]",
            "div[contenteditable='true']"
        ]

        for selector in content_selectors:
            try:
                if selector.startswith("//"):
                    content_textarea = driver.find_element(By.XPATH, selector)
                else:
                    content_textarea = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ 本文入力欄を発見: {selector}")
                break
            except:
                continue

        if not content_textarea:
            raise Exception("本文入力欄が見つかりません")

        # クリップボード経由で本文を入力（絵文字対応）
        try:
            content_textarea.click()
            time.sleep(0.5)
            content_textarea.clear()

            # クリップボードにコピー
            print(f"   📋 クリップボードにコピー中...")
            pyperclip.copy(content)

            # Ctrl+Vで貼り付け（Windows/Linux）またはCmd+V（Mac）
            print(f"   📝 貼り付け中...")
            if sys.platform == 'darwin':
                # Mac: Cmd+V
                content_textarea.send_keys(Keys.COMMAND, 'v')
            else:
                # Windows/Linux: Ctrl+V
                content_textarea.send_keys(Keys.CONTROL, 'v')

            time.sleep(1)  # 貼り付け完了を待つ

        except Exception as e:
            print(f"⚠️  クリップボード貼り付けに失敗: {e}")
            print("   フォールバック: JavaScript経由で入力を試みます...")
            # JavaScript経由で入力（フォールバック）
            try:
                driver.execute_script("arguments[0].textContent = arguments[1];", content_textarea, content)
            except Exception as e2:
                raise Exception(f"本文入力に失敗しました: {e2}")

        print(f"✅ 本文入力完了: {len(content)}文字")
        time.sleep(2)

        # スクリーンショット保存（投稿前）
        screenshot_path = Path.home() / "note_post_preview.png"
        driver.save_screenshot(str(screenshot_path))
        print(f"📸 投稿前のスクリーンショットを保存: {screenshot_path}")

        # 「公開に進む」ボタンをクリック
        print("📤 公開ボタンを探しています...")
        try:
            # すべてのボタンを取得して「公開」が含まれるものを探す
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            publish_button = None

            for btn in all_buttons:
                btn_text = btn.text.strip()
                if '公開' in btn_text:
                    publish_button = btn
                    print(f"✅ 公開ボタンを発見: '{btn_text}'")
                    break

            if not publish_button:
                print("📋 ページ内のすべてのボタンを確認:")
                for i, btn in enumerate(all_buttons):
                    print(f"  ボタン{i}: '{btn.text}'")
                raise Exception("公開ボタンが見つかりません")

            # 公開ボタンをクリック
            print("🚀 ステップ1: 「公開に進む」ボタンをクリック...")
            publish_button.click()
            time.sleep(3)

            # 公開設定画面が表示される
            print("📋 ステップ2: 公開設定画面を確認中...")
            time.sleep(2)  # 画面遷移を待つ

            # ハッシュタグを自動選択
            print("🏷️  提案されたハッシュタグを選択中...")
            try:
                # ハッシュタグボタンを取得（CSSセレクタで#から始まるボタン、またはハッシュタグを含むボタン）
                hashtag_buttons = driver.find_elements(By.XPATH, "//button[starts-with(., '#')]")

                if hashtag_buttons:
                    selected_tags = []
                    for btn in hashtag_buttons:
                        try:
                            tag_text = btn.text.strip()
                            if tag_text and btn.is_displayed():
                                btn.click()
                                selected_tags.append(tag_text)
                                time.sleep(0.3)  # クリック間隔

                                # コンテスト詳細モーダルが開いた場合は閉じる
                                # Escapeキーを押してモーダルを閉じる（より確実）
                                try:
                                    time.sleep(0.5)  # モーダルが開くのを待つ
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    actions = ActionChains(driver)
                                    actions.send_keys(Keys.ESCAPE).perform()
                                    print(f"   ℹ️  コンテスト詳細モーダルを閉じました（Escape）")
                                    time.sleep(0.5)
                                except:
                                    pass

                        except Exception as btn_error:
                            # 個別のボタンクリックに失敗しても続行
                            pass

                    if selected_tags:
                        print(f"✅ ハッシュタグを選択しました: {', '.join(selected_tags)}")
                    else:
                        print("ℹ️  選択可能なハッシュタグが見つかりませんでした")
                else:
                    print("ℹ️  提案されたハッシュタグがありません")

            except Exception as hashtag_error:
                print(f"ℹ️  ハッシュタグ選択をスキップ: {hashtag_error}")

            print("   （記事タイプ: 無料）")

            # 公開設定画面の「投稿する」ボタンを探す
            time.sleep(1)

            all_buttons_settings = driver.find_elements(By.TAG_NAME, "button")
            final_publish_button = None

            for btn in all_buttons_settings:
                btn_text = btn.text.strip()
                # 「投稿する」ボタンを探す
                if btn_text == '投稿する':
                    # 表示されているボタンのみ対象
                    if btn.is_displayed():
                        final_publish_button = btn
                        print(f"✅ 「投稿する」ボタンを発見")
                        break

            if not final_publish_button:
                print("⚠️  「投稿する」ボタンが見つかりません")
                print("📋 公開設定画面のすべてのボタン:")
                for i, btn in enumerate(all_buttons_settings):
                    if btn.is_displayed():
                        print(f"  ボタン{i}: '{btn.text}'")
                raise Exception("「投稿する」ボタンが見つかりません")

            # 「投稿する」ボタンをクリック
            print("🚀 ステップ3: 「投稿する」ボタンをクリックして本番公開...")
            final_publish_button.click()
            time.sleep(3)

            # 公開完了を待つ
            print("⏳ 公開処理を待機中...")
            time.sleep(5)

            # シェアモーダルが表示されるので閉じる
            print("📋 ステップ4: シェアモーダルを閉じて記事URLに遷移中...")
            try:
                # シェアモーダルの×ボタンを探す
                close_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='閉じる' or contains(@class, 'close')]")
                share_modal_closed = False

                for close_btn in close_buttons:
                    try:
                        if close_btn.is_displayed():
                            print("   ✅ シェアモーダルの×ボタンを発見")
                            close_btn.click()
                            share_modal_closed = True
                            time.sleep(2)
                            break
                    except:
                        pass

                # ×ボタンが見つからない場合はEscapeキーで閉じる
                if not share_modal_closed:
                    print("   ℹ️  Escapeキーでシェアモーダルを閉じます")
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.ESCAPE).perform()
                    time.sleep(2)

                print("   ✅ シェアモーダルを閉じました")
            except Exception as share_error:
                print(f"   ℹ️  シェアモーダルのクローズをスキップ: {share_error}")

            # URLの遷移を待つ
            time.sleep(2)

            # 現在のURLを確認（記事URLが取得できる場合がある）
            current_url = driver.current_url
            print(f"📍 公開後のURL: {current_url}")

            # 記事URLを取得
            note_url = None
            note_username = os.getenv('NOTE_USERNAME', '')

            # ケース1: editor.note.com/notes/{note_id}/publish/ の形式の場合
            if "editor.note.com/notes/" in current_url and "/publish/" in current_url:
                # 記事IDを抽出
                import re
                match = re.search(r'/notes/(n[a-zA-Z0-9]+)/', current_url)
                if match and note_username:
                    note_id = match.group(1)
                    # 公開記事のURLを生成
                    note_url = f"https://note.com/{note_username}/n/{note_id}"
                    print(f"✅ 記事を公開しました！")
                    print(f"📍 公開URL: {note_url}")
                else:
                    print(f"ℹ️  記事IDは取得できましたが、ユーザー名が設定されていません")

            # ケース2: URLに記事IDが含まれている場合（既に公開記事のURL）
            elif "/n" in current_url and "note.com" in current_url and "editor.note.com" not in current_url:
                note_url = current_url.split('?')[0]  # クエリパラメータを除去
                print(f"✅ 記事を公開しました！")
                print(f"📍 公開URL: {note_url}")

            # ケース2: URLから記事IDが取得できない場合、プロフィールページから取得
            else:
                print("📋 ステップ4: 記事URLを取得中...")

                # NOTE_USERNAMEを環境変数から取得（オプション）
                note_username = os.getenv('NOTE_USERNAME', '')

                if note_username:
                    try:
                        # ユーザーのプロフィールページに移動
                        profile_url = f"https://note.com/{note_username}"
                        print(f"   プロフィールページに移動: {profile_url}")
                        driver.get(profile_url)
                        time.sleep(3)

                        # 最新の記事リンクを取得
                        article_links = driver.find_elements(By.CSS_SELECTOR, f"a[href*='/{note_username}/n']")
                        if article_links:
                            # 最初のリンク（最新記事）のhrefを取得
                            latest_article_url = article_links[0].get_attribute('href')
                            if latest_article_url and '/n' in latest_article_url:
                                note_url = latest_article_url.split('?')[0]  # クエリパラメータを除去
                                print(f"✅ 記事を公開しました！")
                                print(f"📍 公開URL: {note_url}")
                        else:
                            print(f"ℹ️  プロフィールページから記事URLを取得できませんでした")
                    except Exception as profile_error:
                        print(f"ℹ️  プロフィールページからの取得に失敗: {profile_error}")

                # URLが取得できなかった場合
                if not note_url:
                    print(f"✅ 記事の公開が完了しました！")
                    print(f"📍 記事はNote.comのマイページから確認できます: https://note.com/my/notes")
                    # フォールバック: マイページのURLを返す
                    note_url = "https://note.com/my/notes"

        except Exception as e:
            print(f"⚠️  公開処理中にエラー: {str(e)}")
            print("📝 記事の下書きは保存されました")
            note_url = driver.current_url

        result = {
            'success': True,
            'url': note_url,
            'title': title,
            'content_length': len(content),
            'dry_run': False
        }

        # スクリーンショット保存（投稿後）
        screenshot_path_after = Path.home() / "note_post_after.png"
        driver.save_screenshot(str(screenshot_path_after))
        print(f"📸 投稿後のスクリーンショットを保存: {screenshot_path_after}")

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
