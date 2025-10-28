#!/usr/bin/env python3
"""
SNS自動投稿システム - メイン統合スクリプト

各プラットフォームへの投稿を一括で実行します。
"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from x_platform.post_x import post_to_x
from note_platform.post_note import post_to_note


def read_text_file(file_path: str) -> str:
    """
    テキストファイルを読み込む（UTF-8）

    Args:
        file_path: 読み込むファイルのパス

    Returns:
        str: ファイルの内容

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        Exception: その他のエラー
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        return path.read_text(encoding='utf-8').strip()
    except Exception as e:
        raise Exception(f"ファイル読み込みエラー ({file_path}): {e}")


def parse_post_file(file_path: str) -> dict:
    """
    統合投稿ファイルをパースする

    ファイル形式:
    [X]
    X投稿のテキスト

    [Note Title]
    Noteのタイトル

    [Note Content]
    Noteの本文
    複数行もOK

    Args:
        file_path: 投稿ファイルのパス

    Returns:
        dict: {'x_text': str, 'note_title': str, 'note_content': str}
              各値はNoneの可能性あり

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        Exception: その他のエラー
    """
    try:
        content = read_text_file(file_path)
        result = {
            'x_text': None,
            'note_title': None,
            'note_content': None
        }

        # セクションで分割
        current_section = None
        section_content = []

        for line in content.split('\n'):
            # セクション見出しをチェック
            if line.strip() == '[X]':
                # 前のセクションを保存
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                current_section = 'x_text'
                section_content = []
            elif line.strip() == '[Note Title]':
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                current_section = 'note_title'
                section_content = []
            elif line.strip() == '[Note Content]':
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()
                current_section = 'note_content'
                section_content = []
            else:
                # セクションの内容
                if current_section:
                    section_content.append(line)

        # 最後のセクションを保存
        if current_section:
            result[current_section] = '\n'.join(section_content).strip()

        # 空文字列をNoneに変換
        for key in result:
            if result[key] == '':
                result[key] = None

        return result

    except Exception as e:
        raise Exception(f"投稿ファイルパースエラー ({file_path}): {e}")


def post_to_all_platforms(
    x_text: str = None,
    note_title: str = None,
    note_content: str = None,
    dry_run: bool = False,
    note_headless: bool = False
):
    """
    すべてのプラットフォームに投稿

    Args:
        x_text: X投稿用のテキスト（Noneの場合はスキップ）
        note_title: Note投稿用のタイトル（Noneの場合はスキップ）
        note_content: Note投稿用の本文（Noneの場合はスキップ）
        dry_run: Trueの場合、実際には投稿しない
        note_headless: Noteをヘッドレスモードで実行

    Returns:
        dict: 各プラットフォームの投稿結果
    """
    results = {}

    # X投稿
    if x_text:
        print("=" * 80)
        print("📱 X (Twitter) に投稿中...")
        print("=" * 80)
        try:
            x_result = post_to_x(x_text, dry_run=dry_run)
            results['x'] = x_result

            if x_result['dry_run']:
                print("✅ X投稿 [DRY RUN] 完了")
            else:
                print(f"✅ X投稿完了: {x_result['url']}")
        except Exception as e:
            results['x'] = {'success': False, 'error': str(e)}
            print(f"❌ X投稿失敗: {e}")
        print()
    else:
        print("⏭️  X投稿をスキップ（テキストが指定されていません）\n")

    # Note投稿
    if note_title and note_content:
        print("=" * 80)
        print("📝 Note.com に投稿中...")
        print("=" * 80)
        try:
            note_result = post_to_note(
                title=note_title,
                content=note_content,
                headless=note_headless,
                dry_run=dry_run
            )
            results['note'] = note_result

            if note_result['dry_run']:
                print("✅ Note投稿 [DRY RUN] 完了")
            else:
                print(f"✅ Note投稿完了: {note_result['url']}")
        except Exception as e:
            results['note'] = {'success': False, 'error': str(e)}
            print(f"❌ Note投稿失敗: {e}")
        print()
    else:
        print("⏭️  Note投稿をスキップ（タイトルまたは本文が指定されていません）\n")

    return results


def main():
    """コマンドラインインターフェース"""
    parser = argparse.ArgumentParser(
        description='SNS自動投稿システム - 各プラットフォームに一括投稿',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 統合投稿ファイルを使用（推奨）
  python main.py --post-file "posts/post.txt"

  # X投稿のみ
  python main.py --post-file "posts/post.txt"  # [X]セクションのみ記載

  # 統合ファイルでDry run
  python main.py --post-file "posts/post.txt" --dry-run

  # 従来の方法（個別ファイル指定も可能）
  python main.py --x-text-file "posts/x_post.txt"

  # 直接テキストを指定
  python main.py --x-text "今日はPythonでAPIを実装しました 🚀"

投稿ファイルの形式:
  [X]
  X投稿のテキスト

  [Note Title]
  Noteのタイトル

  [Note Content]
  Noteの本文
  複数行もOK

注意:
  - テキストファイルは UTF-8 エンコーディングで保存してください
  - X投稿は WSL/Linux/Windows で動作します
  - Note投稿は Windows環境のみで動作します
  - 各プラットフォームの認証情報は .env に設定してください
        """
    )

    # 統合投稿ファイル（推奨）
    parser.add_argument(
        '--post-file',
        type=str,
        help='統合投稿ファイルのパス（[X]、[Note Title]、[Note Content]セクションで記述）'
    )

    # X投稿オプション（個別指定）
    parser.add_argument(
        '--x-text',
        type=str,
        help='X (Twitter) に投稿するテキスト'
    )
    parser.add_argument(
        '--x-text-file',
        type=str,
        help='X (Twitter) に投稿するテキストのファイルパス'
    )

    # Note投稿オプション（個別指定）
    parser.add_argument(
        '--note-title',
        type=str,
        help='Note.com に投稿する記事のタイトル'
    )
    parser.add_argument(
        '--note-title-file',
        type=str,
        help='Note.com に投稿する記事のタイトルのファイルパス'
    )
    parser.add_argument(
        '--note-content',
        type=str,
        help='Note.com に投稿する記事の本文'
    )
    parser.add_argument(
        '--note-content-file',
        type=str,
        help='Note.com に投稿する記事の本文のファイルパス'
    )
    parser.add_argument(
        '--note-headless',
        action='store_true',
        help='Noteをヘッドレスモードで実行'
    )

    # 共通オプション
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には投稿せず、シミュレーションのみ'
    )

    args = parser.parse_args()

    # ファイルから読み込む（ファイルが指定されている場合）
    x_text = None
    note_title = None
    note_content = None

    try:
        # 統合投稿ファイルを使用する場合
        if args.post_file:
            print(f"📄 統合投稿ファイルを読み込み: {args.post_file}")
            parsed = parse_post_file(args.post_file)
            x_text = parsed['x_text']
            note_title = parsed['note_title']
            note_content = parsed['note_content']

            # 読み込んだ内容を表示
            if x_text:
                print(f"  ✓ [X] セクション: {len(x_text)}文字")
            if note_title:
                print(f"  ✓ [Note Title] セクション: {len(note_title)}文字")
            if note_content:
                print(f"  ✓ [Note Content] セクション: {len(note_content)}文字")

        # 個別ファイル/テキスト指定の場合
        else:
            # X投稿のテキスト
            if args.x_text_file:
                print(f"📄 X投稿テキストを読み込み: {args.x_text_file}")
                x_text = read_text_file(args.x_text_file)
            elif args.x_text:
                x_text = args.x_text

            # Noteのタイトル
            if args.note_title_file:
                print(f"📄 Noteタイトルを読み込み: {args.note_title_file}")
                note_title = read_text_file(args.note_title_file)
            elif args.note_title:
                note_title = args.note_title

            # Noteの本文
            if args.note_content_file:
                print(f"📄 Note本文を読み込み: {args.note_content_file}")
                note_content = read_text_file(args.note_content_file)
            elif args.note_content:
                note_content = args.note_content

    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        sys.exit(1)

    # 少なくとも1つのプラットフォームが指定されているか確認
    if not x_text and not (note_title and note_content):
        parser.error("少なくとも1つのプラットフォームの投稿内容を指定してください\n"
                     "  推奨: --post-file でセクション形式のファイルを指定\n"
                     "  または: --x-text/--x-text-file または --note-title/--note-title-file & --note-content/--note-content-file")

    print("=" * 80)
    print("🚀 SNS自動投稿システム")
    print("=" * 80)
    if args.dry_run:
        print("🔍 [DRY RUN MODE] 実際には投稿しません")
    print()

    try:
        # 投稿実行
        results = post_to_all_platforms(
            x_text=x_text,
            note_title=note_title,
            note_content=note_content,
            dry_run=args.dry_run,
            note_headless=args.note_headless
        )

        # 結果サマリー
        print("=" * 80)
        print("📊 投稿結果サマリー")
        print("=" * 80)

        if 'x' in results:
            status = "✅ 成功" if results['x'].get('success') else "❌ 失敗"
            print(f"X (Twitter): {status}")
            if results['x'].get('url'):
                print(f"  URL: {results['x']['url']}")

        if 'note' in results:
            status = "✅ 成功" if results['note'].get('success') else "❌ 失敗"
            print(f"Note.com: {status}")
            if results['note'].get('url'):
                print(f"  URL: {results['note']['url']}")

        print()

        # エラーがあった場合は終了コード1
        if any(not r.get('success', True) for r in results.values()):
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  ユーザーによって中断されました")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
