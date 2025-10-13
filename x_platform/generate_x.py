#!/usr/bin/env python3
"""
X投稿文生成モジュール
Gemini APIを使用して、活動内容から魅力的なX投稿文を生成
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()


def generate_x_post(activity_content: str, max_length: int = None) -> str:
    """
    活動内容からX投稿文を生成

    Args:
        activity_content: 活動内容
        max_length: 投稿文の最大文字数（Noneの場合は制限なし、Xプレミアム向け）

    Returns:
        生成されたX投稿文

    Raises:
        ValueError: APIキーが設定されていない場合
        Exception: API呼び出しに失敗した場合
    """
    # APIキー確認
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEYを.envに設定してください')

    # Gemini API設定
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # プロンプト作成（文字数制限の有無で分岐）
    if max_length:
        length_instruction = f"- 最大{max_length}文字以内に収める"
    else:
        length_instruction = "- 文字数制限なし（Xプレミアム対応）。情報量を重視し、詳細かつ具体的に記述"

    prompt = f"""以下の活動内容から、Xに投稿する魅力的で情報価値の高い文章を作成してください。

【活動内容】
{activity_content}

【投稿文作成の指示】
{length_instruction}
- 技術的な内容は具体的に記述（技術名、バージョン、手法など）
- 実装の詳細や工夫したポイントを盛り込む
- 「何を」「どのように」「なぜ」「結果」を明確に
- カジュアルで親しみやすい口調を保ちつつ、専門性も感じさせる
- ハッシュタグを2-3個含める（技術スタック関連）
- 絵文字は控えめに使用（多用しない）
- 改行と段落分けで読みやすく構成
- 箇条書きを活用して情報を整理
- 読者が「詳しく知りたい」「参考になる」と感じる内容に

【投稿のトーン】
- エンジニア・開発者向けの有益な情報を提供
- 実装の苦労や学びを共有する姿勢
- 自慢げにならず、謙虚で共感を呼ぶ表現
- 技術コミュニティに貢献する意識

投稿文のみを出力してください（説明や前置きは不要）。"""

    try:
        # API呼び出し
        response = model.generate_content(prompt)
        generated_text = response.text.strip()

        # 文字数チェック（制限がある場合のみ）
        if max_length and len(generated_text) > max_length:
            print(f"⚠️  生成された文章が{max_length}文字を超えています（{len(generated_text)}文字）")
            print("   自動的に切り詰めます...")
            generated_text = generated_text[:max_length-3] + "..."

        return generated_text

    except Exception as e:
        raise Exception(f"X投稿文の生成に失敗しました: {str(e)}")


def main():
    """コマンドラインインターフェース"""
    import argparse

    parser = argparse.ArgumentParser(
        description='活動内容からX投稿文を生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python generate_x.py "今日はPythonでAPIを実装しました"
  python generate_x.py "新しいプロジェクトを開始" --max-length 140
        """
    )

    parser.add_argument(
        'content',
        help='活動内容'
    )

    parser.add_argument(
        '--max-length',
        type=int,
        default=None,
        help='投稿文の最大文字数（指定しない場合は制限なし＝Xプレミアム向け）'
    )

    args = parser.parse_args()

    try:
        print(f"🤖 Gemini APIで投稿文を生成中...")
        print(f"📝 活動内容: {args.content}")
        print()

        # 投稿文生成
        post_text = generate_x_post(args.content, args.max_length)

        # 結果表示
        print("=" * 60)
        print("✅ X投稿文が生成されました")
        print("=" * 60)
        print(post_text)
        print("=" * 60)
        if args.max_length:
            print(f"📊 文字数: {len(post_text)}/{args.max_length}")
        else:
            print(f"📊 文字数: {len(post_text)} (制限なし)")
        print()

    except ValueError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
