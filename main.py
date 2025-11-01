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
from qiita_platform.post_qiita import post_to_qiita
from zenn_platform.post_zenn import post_to_zenn
from zenn_platform.post_zenn_github import post_to_zenn_github
from gemini_formatter import GeminiFormatter


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

    [Qiita Title]
    Qiitaのタイトル

    [Qiita Content]
    Qiitaの本文（マークダウン）
    複数行もOK

    [Qiita Tags]
    Python, API, 自動化

    [Zenn Title]
    Zennのタイトル

    [Zenn Content]
    Zennの本文（マークダウン）
    複数行もOK

    [Zenn Emoji]
    📝

    [Zenn Topics]
    Python, API, 自動化

    Args:
        file_path: 投稿ファイルのパス

    Returns:
        dict: {'x_text': str, 'note_title': str, 'note_content': str,
               'qiita_title': str, 'qiita_content': str, 'qiita_tags': List[str],
               'zenn_title': str, 'zenn_content': str, 'zenn_emoji': str, 'zenn_topics': List[str]}
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
            'note_content': None,
            'qiita_title': None,
            'qiita_content': None,
            'qiita_tags': None,
            'zenn_title': None,
            'zenn_content': None,
            'zenn_emoji': None,
            'zenn_topics': None
        }

        # セクションで分割
        current_section = None
        section_content = []

        for line in content.split('\n'):
            # セクション見出しをチェック（[で始まり]で終わる行）
            stripped_line = line.strip()

            if stripped_line.startswith('[') and stripped_line.endswith(']'):
                # 前のセクションを保存
                if current_section:
                    result[current_section] = '\n'.join(section_content).strip()

                # 認識するセクション見出しのみ処理
                if stripped_line == '[X]':
                    current_section = 'x_text'
                    section_content = []
                elif stripped_line == '[Note Title]':
                    current_section = 'note_title'
                    section_content = []
                elif stripped_line == '[Note Content]':
                    current_section = 'note_content'
                    section_content = []
                elif stripped_line == '[Qiita Title]':
                    current_section = 'qiita_title'
                    section_content = []
                elif stripped_line == '[Qiita Content]':
                    current_section = 'qiita_content'
                    section_content = []
                elif stripped_line == '[Qiita Tags]':
                    current_section = 'qiita_tags'
                    section_content = []
                elif stripped_line == '[Zenn Title]':
                    current_section = 'zenn_title'
                    section_content = []
                elif stripped_line == '[Zenn Content]':
                    current_section = 'zenn_content'
                    section_content = []
                elif stripped_line == '[Zenn Emoji]':
                    current_section = 'zenn_emoji'
                    section_content = []
                elif stripped_line == '[Zenn Topics]':
                    current_section = 'zenn_topics'
                    section_content = []
                else:
                    # 認識しないセクション見出しが来たら終了
                    current_section = None
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

        # Qiitaタグをカンマ区切りの文字列からリストに変換
        if result['qiita_tags']:
            result['qiita_tags'] = [tag.strip() for tag in result['qiita_tags'].split(',') if tag.strip()]
            # タグが空リストならNoneに変換
            if not result['qiita_tags']:
                result['qiita_tags'] = None

        # Zennトピックをカンマ区切りの文字列からリストに変換
        if result['zenn_topics']:
            result['zenn_topics'] = [topic.strip() for topic in result['zenn_topics'].split(',') if topic.strip()]
            # トピックが空リストならNoneに変換
            if not result['zenn_topics']:
                result['zenn_topics'] = None

        return result

    except Exception as e:
        raise Exception(f"投稿ファイルパースエラー ({file_path}): {e}")


def post_to_all_platforms(
    x_text: str = None,
    note_title: str = None,
    note_content: str = None,
    qiita_title: str = None,
    qiita_content: str = None,
    qiita_tags: list = None,
    qiita_private: bool = False,
    qiita_tweet: bool = False,
    zenn_title: str = None,
    zenn_content: str = None,
    zenn_emoji: str = None,
    zenn_topics: list = None,
    zenn_published: bool = True,
    zenn_type: str = "tech",
    zenn_slug: str = None,
    zenn_use_github: bool = False,
    dry_run: bool = False,
    note_headless: bool = False,
    zenn_headless: bool = False,
    use_gemini: bool = False
):
    """
    すべてのプラットフォームに投稿

    Args:
        x_text: X投稿用のテキスト（Noneの場合はスキップ）
        note_title: Note投稿用のタイトル（Noneの場合はスキップ）
        note_content: Note投稿用の本文（Noneの場合はスキップ）
        qiita_title: Qiita投稿用のタイトル（Noneの場合はスキップ）
        qiita_content: Qiita投稿用の本文（Noneの場合はスキップ）
        qiita_tags: Qiita投稿用のタグリスト（Noneの場合は空リスト）
        qiita_private: Qiitaを限定共有記事として投稿
        qiita_tweet: QiitaでTwitter連携投稿
        zenn_title: Zenn投稿用のタイトル（Noneの場合はスキップ）
        zenn_content: Zenn投稿用の本文（Noneの場合はスキップ）
        zenn_emoji: Zenn投稿用の絵文字アイコン（デフォルト: 📝）
        zenn_topics: Zenn投稿用のトピックリスト（Noneの場合は空リスト）
        zenn_published: Zennを公開記事として投稿（Falseで下書き）
        zenn_type: Zenn記事タイプ（"tech" or "idea"、デフォルト: "tech"）
        zenn_slug: Zenn記事のスラッグ（省略時は自動生成）
        zenn_use_github: TrueでGitHub連携方式、FalseでSelenium方式
        dry_run: Trueの場合、実際には投稿しない
        note_headless: Noteをヘッドレスモードで実行
        zenn_headless: Zennをヘッドレスモードで実行（Selenium方式のみ）
        use_gemini: Trueの場合、Gemini APIで文章を整形

    Returns:
        dict: 各プラットフォームの投稿結果
    """
    results = {}

    # Gemini APIで整形
    if use_gemini:
        try:
            print("=" * 80)
            print("🤖 Gemini APIで投稿内容を整形中...")
            print("=" * 80)
            formatter = GeminiFormatter()
            formatted = formatter.format_all(
                x_text=x_text,
                note_title=note_title,
                note_content=note_content
            )

            # 整形結果を反映
            if formatted['x_text']:
                x_text = formatted['x_text']
            if formatted['note_title']:
                note_title = formatted['note_title']
            if formatted['note_content']:
                note_content = formatted['note_content']

            print("✅ 整形完了")
            print()
        except Exception as e:
            print(f"⚠️  Gemini整形に失敗: {e}")
            print("   元の文章で投稿を続行します...")
            print()

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

    # Qiita投稿
    if qiita_title and qiita_content:
        print("=" * 80)
        print("📚 Qiita に投稿中...")
        print("=" * 80)
        try:
            qiita_result = post_to_qiita(
                title=qiita_title,
                content=qiita_content,
                tags=qiita_tags,
                private=qiita_private,
                tweet=qiita_tweet,
                dry_run=dry_run
            )
            results['qiita'] = qiita_result

            if qiita_result['dry_run']:
                print("✅ Qiita投稿 [DRY RUN] 完了")
            else:
                print(f"✅ Qiita投稿完了: {qiita_result['url']}")
        except Exception as e:
            results['qiita'] = {'success': False, 'error': str(e)}
            print(f"❌ Qiita投稿失敗: {e}")
        print()
    else:
        print("⏭️  Qiita投稿をスキップ（タイトルまたは本文が指定されていません）\n")

    # Zenn投稿
    if zenn_title and zenn_content:
        print("=" * 80)
        if zenn_use_github:
            print("⚡ Zenn に投稿中（GitHub連携方式）...")
        else:
            print("⚡ Zenn に投稿中（Selenium方式）...")
        print("=" * 80)
        try:
            if zenn_use_github:
                # GitHub連携方式
                zenn_result = post_to_zenn_github(
                    title=zenn_title,
                    content=zenn_content,
                    emoji=zenn_emoji if zenn_emoji else "📝",
                    article_type=zenn_type,
                    topics=zenn_topics,
                    published=zenn_published,
                    slug=zenn_slug,
                    dry_run=dry_run
                )
            else:
                # Selenium方式
                zenn_result = post_to_zenn(
                    title=zenn_title,
                    content=zenn_content,
                    emoji=zenn_emoji if zenn_emoji else "📝",
                    topics=zenn_topics,
                    published=zenn_published,
                    headless=zenn_headless,
                    dry_run=dry_run
                )
            results['zenn'] = zenn_result

            if zenn_result['dry_run']:
                print("✅ Zenn投稿 [DRY RUN] 完了")
            else:
                if zenn_use_github:
                    print(f"✅ Zenn投稿完了（GitHub連携）: {zenn_result.get('file_path', 'N/A')}")
                else:
                    print(f"✅ Zenn投稿完了: {zenn_result['url']}")
        except Exception as e:
            results['zenn'] = {'success': False, 'error': str(e)}
            print(f"❌ Zenn投稿失敗: {e}")
        print()
    else:
        print("⏭️  Zenn投稿をスキップ（タイトルまたは本文が指定されていません）\n")

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

  [Qiita Title]
  Qiitaのタイトル

  [Qiita Content]
  Qiitaの本文（マークダウン）
  複数行もOK

  [Qiita Tags]
  Python, API, 自動化

  [Zenn Title]
  Zennのタイトル

  [Zenn Content]
  Zennの本文（マークダウン）
  複数行もOK

  [Zenn Emoji]
  📝

  [Zenn Topics]
  Python, API, 自動化

注意:
  - テキストファイルは UTF-8 エンコーディングで保存してください
  - X投稿は WSL/Linux/Windows で動作します
  - Note投稿は Windows環境のみで動作します（Selenium使用）
  - Qiita投稿は Qiita API v2を使用します
  - Zenn投稿は Windows環境のみで動作します（Selenium使用）
  - 各プラットフォームの認証情報は .env に設定してください
        """
    )

    # 統合投稿ファイル（推奨）
    parser.add_argument(
        '--post-file',
        type=str,
        help='統合投稿ファイルのパス（[X]、[Note Title]、[Note Content]、[Qiita Title]、[Qiita Content]、[Qiita Tags]、[Zenn Title]、[Zenn Content]、[Zenn Emoji]、[Zenn Topics]セクションで記述）'
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

    # Qiita投稿オプション（個別指定）
    parser.add_argument(
        '--qiita-title',
        type=str,
        help='Qiita に投稿する記事のタイトル'
    )
    parser.add_argument(
        '--qiita-title-file',
        type=str,
        help='Qiita に投稿する記事のタイトルのファイルパス'
    )
    parser.add_argument(
        '--qiita-content',
        type=str,
        help='Qiita に投稿する記事の本文（マークダウン）'
    )
    parser.add_argument(
        '--qiita-content-file',
        type=str,
        help='Qiita に投稿する記事の本文のファイルパス'
    )
    parser.add_argument(
        '--qiita-tags',
        type=str,
        nargs='+',
        help='Qiita に投稿する記事のタグ（スペース区切り、例: Python API 自動化）'
    )
    parser.add_argument(
        '--qiita-private',
        action='store_true',
        help='Qiita記事を限定共有として投稿'
    )
    parser.add_argument(
        '--qiita-tweet',
        action='store_true',
        help='QiitaでTwitter連携投稿を有効化'
    )

    # Zenn投稿オプション（個別指定）
    parser.add_argument(
        '--zenn-title',
        type=str,
        help='Zenn に投稿する記事のタイトル'
    )
    parser.add_argument(
        '--zenn-title-file',
        type=str,
        help='Zenn に投稿する記事のタイトルのファイルパス'
    )
    parser.add_argument(
        '--zenn-content',
        type=str,
        help='Zenn に投稿する記事の本文（マークダウン）'
    )
    parser.add_argument(
        '--zenn-content-file',
        type=str,
        help='Zenn に投稿する記事の本文のファイルパス'
    )
    parser.add_argument(
        '--zenn-emoji',
        type=str,
        default='📝',
        help='Zenn に投稿する記事の絵文字アイコン（デフォルト: 📝）'
    )
    parser.add_argument(
        '--zenn-topics',
        type=str,
        nargs='+',
        help='Zenn に投稿する記事のトピック（スペース区切り、例: Python API 自動化、最大5個）'
    )
    parser.add_argument(
        '--zenn-type',
        type=str,
        default='tech',
        choices=['tech', 'idea'],
        help='Zenn記事のタイプ（デフォルト: tech）'
    )
    parser.add_argument(
        '--zenn-slug',
        type=str,
        help='Zenn記事のスラッグ（省略時は自動生成、12-50文字）'
    )
    parser.add_argument(
        '--zenn-draft',
        action='store_true',
        help='Zenn記事を下書きとして保存（公開しない）'
    )
    parser.add_argument(
        '--zenn-github',
        action='store_true',
        help='ZennをGitHub連携方式で投稿（デフォルトはSelenium方式）'
    )
    parser.add_argument(
        '--zenn-headless',
        action='store_true',
        help='Zennをヘッドレスモードで実行（Selenium方式のみ）'
    )

    # 共通オプション
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='実際には投稿せず、シミュレーションのみ'
    )
    parser.add_argument(
        '--use-gemini',
        action='store_true',
        help='Gemini APIで投稿内容を各プラットフォームに適した形式に整形'
    )

    args = parser.parse_args()

    # ファイルから読み込む（ファイルが指定されている場合）
    x_text = None
    note_title = None
    note_content = None
    qiita_title = None
    qiita_content = None
    qiita_tags = None
    zenn_title = None
    zenn_content = None
    zenn_emoji = None
    zenn_topics = None

    try:
        # 統合投稿ファイルを使用する場合
        if args.post_file:
            print(f"📄 統合投稿ファイルを読み込み: {args.post_file}")
            parsed = parse_post_file(args.post_file)
            x_text = parsed['x_text']
            note_title = parsed['note_title']
            note_content = parsed['note_content']
            qiita_title = parsed['qiita_title']
            qiita_content = parsed['qiita_content']
            qiita_tags = parsed['qiita_tags']
            zenn_title = parsed['zenn_title']
            zenn_content = parsed['zenn_content']
            zenn_emoji = parsed['zenn_emoji']
            zenn_topics = parsed['zenn_topics']

            # 読み込んだ内容を表示
            if x_text:
                print(f"  ✓ [X] セクション: {len(x_text)}文字")
            if note_title:
                print(f"  ✓ [Note Title] セクション: {len(note_title)}文字")
            if note_content:
                print(f"  ✓ [Note Content] セクション: {len(note_content)}文字")
            if qiita_title:
                print(f"  ✓ [Qiita Title] セクション: {len(qiita_title)}文字")
            if qiita_content:
                print(f"  ✓ [Qiita Content] セクション: {len(qiita_content)}文字")
            if qiita_tags:
                print(f"  ✓ [Qiita Tags] セクション: {', '.join(qiita_tags)}")
            if zenn_title:
                print(f"  ✓ [Zenn Title] セクション: {len(zenn_title)}文字")
            if zenn_content:
                print(f"  ✓ [Zenn Content] セクション: {len(zenn_content)}文字")
            if zenn_emoji:
                print(f"  ✓ [Zenn Emoji] セクション: {zenn_emoji}")
            if zenn_topics:
                print(f"  ✓ [Zenn Topics] セクション: {', '.join(zenn_topics)}")

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

            # Qiitaのタイトル
            if args.qiita_title_file:
                print(f"📄 Qiitaタイトルを読み込み: {args.qiita_title_file}")
                qiita_title = read_text_file(args.qiita_title_file)
            elif args.qiita_title:
                qiita_title = args.qiita_title

            # Qiitaの本文
            if args.qiita_content_file:
                print(f"📄 Qiita本文を読み込み: {args.qiita_content_file}")
                qiita_content = read_text_file(args.qiita_content_file)
            elif args.qiita_content:
                qiita_content = args.qiita_content

            # Qiitaのタグ
            if args.qiita_tags:
                qiita_tags = args.qiita_tags

            # Zennのタイトル
            if args.zenn_title_file:
                print(f"📄 Zennタイトルを読み込み: {args.zenn_title_file}")
                zenn_title = read_text_file(args.zenn_title_file)
            elif args.zenn_title:
                zenn_title = args.zenn_title

            # Zennの本文
            if args.zenn_content_file:
                print(f"📄 Zenn本文を読み込み: {args.zenn_content_file}")
                zenn_content = read_text_file(args.zenn_content_file)
            elif args.zenn_content:
                zenn_content = args.zenn_content

            # Zennの絵文字
            if args.zenn_emoji:
                zenn_emoji = args.zenn_emoji

            # Zennのトピック
            if args.zenn_topics:
                zenn_topics = args.zenn_topics

    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        sys.exit(1)

    # 少なくとも1つのプラットフォームが指定されているか確認
    if not x_text and not (note_title and note_content) and not (qiita_title and qiita_content) and not (zenn_title and zenn_content):
        parser.error("少なくとも1つのプラットフォームの投稿内容を指定してください\n"
                     "  推奨: --post-file でセクション形式のファイルを指定\n"
                     "  または: --x-text/--x-text-file または --note-title/--note-title-file & --note-content/--note-content-file または --qiita-title/--qiita-title-file & --qiita-content/--qiita-content-file または --zenn-title/--zenn-title-file & --zenn-content/--zenn-content-file")

    print("=" * 80)
    print("🚀 SNS自動投稿システム")
    print("=" * 80)
    if args.dry_run:
        print("🔍 [DRY RUN MODE] 実際には投稿しません")
    if args.use_gemini:
        print("🤖 [GEMINI MODE] Gemini APIで文章を整形します")
    print()

    try:
        # 投稿実行
        results = post_to_all_platforms(
            x_text=x_text,
            note_title=note_title,
            note_content=note_content,
            qiita_title=qiita_title,
            qiita_content=qiita_content,
            qiita_tags=qiita_tags,
            qiita_private=args.qiita_private if hasattr(args, 'qiita_private') else False,
            qiita_tweet=args.qiita_tweet if hasattr(args, 'qiita_tweet') else False,
            zenn_title=zenn_title,
            zenn_content=zenn_content,
            zenn_emoji=zenn_emoji,
            zenn_topics=zenn_topics,
            zenn_published=not args.zenn_draft if hasattr(args, 'zenn_draft') else True,
            zenn_type=args.zenn_type if hasattr(args, 'zenn_type') else 'tech',
            zenn_slug=args.zenn_slug if hasattr(args, 'zenn_slug') else None,
            zenn_use_github=args.zenn_github if hasattr(args, 'zenn_github') else False,
            dry_run=args.dry_run,
            note_headless=args.note_headless,
            zenn_headless=args.zenn_headless if hasattr(args, 'zenn_headless') else False,
            use_gemini=args.use_gemini
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

        if 'qiita' in results:
            status = "✅ 成功" if results['qiita'].get('success') else "❌ 失敗"
            print(f"Qiita: {status}")
            if results['qiita'].get('url'):
                print(f"  URL: {results['qiita']['url']}")

        if 'zenn' in results:
            status = "✅ 成功" if results['zenn'].get('success') else "❌ 失敗"
            print(f"Zenn: {status}")
            if results['zenn'].get('url'):
                print(f"  URL: {results['zenn']['url']}")

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
