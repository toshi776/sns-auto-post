#!/usr/bin/env python3
"""
Note記事生成モジュール
Gemini APIを使用して、活動内容から詳細なNote記事を生成
"""

import os
import sys
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import google.generativeai as genai

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

# 環境変数読み込み
load_dotenv()


def generate_note_article(activity_content: str, style: str = "technical") -> Dict[str, str]:
    """
    活動内容からNote記事を生成

    Args:
        activity_content: 活動内容
        style: 記事のスタイル（"technical": 技術記事、"casual": カジュアル、"tutorial": チュートリアル）

    Returns:
        Dict[str, str]: {'title': タイトル, 'content': 本文}

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

    # スタイル別のプロンプト設定
    style_instructions = {
        "technical": """
- エンジニア・開発者向けの技術記事
- 実装の詳細、コード例、技術的な工夫を詳しく解説
- 「〜です・ます」調の丁寧な文体
- 図解や箇条書きを活用
- 読者が実際に実装できるレベルの詳細さ
        """,
        "casual": """
- 幅広い読者向けのカジュアルな記事
- 難しい用語は噛み砕いて説明
- 「〜です・ます」調だが親しみやすい文体
- 体験談や感想を交える
- 読みやすさを重視
        """,
        "tutorial": """
- 初心者向けのチュートリアル記事
- ステップバイステップで解説
- 「〜しましょう」という呼びかけ口調
- 各ステップに具体例を含める
- トラブルシューティングも記載
        """
    }

    style_instruction = style_instructions.get(style, style_instructions["technical"])

    # プロンプト作成
    prompt = f"""以下の活動内容から、Note.comに投稿する詳細な技術記事を作成してください。

【活動内容】
{activity_content}

【記事作成の指示】
{style_instruction}

【記事の構成】
1. **タイトル**
   - 興味を引く、わかりやすいタイトル
   - 30-50文字程度
   - 「〜してみた」「〜を実装した話」などの形式も可

2. **本文の構成**
   以下のセクションを含めてください：

   ## はじめに
   - 記事の概要と背景
   - なぜこれを作ったのか

   ## 実装内容
   - 何を実装したか
   - 技術スタック
   - アーキテクチャ概要

   ## 実装の詳細
   - 具体的な実装方法
   - コード例（マークダウンのコードブロック形式）
   - 工夫したポイント

   ## 苦労した点・学び
   - 実装中の課題
   - 解決方法
   - 得られた知見

   ## 今後の展望
   - 次のステップ
   - 改善したい点

   ## まとめ
   - 記事の総括
   - 読者へのメッセージ

【本文の要件】
- 2000-4000文字程度の詳細な記事
- マークダウン形式で記述
- 見出しは ## で表現
- コードブロックは ```言語名 で記述
- 箇条書きは - で記述
- 技術用語は正確に、必要に応じて説明を加える
- 絵文字は見出しに控えめに使用（本文では使わない）
- 専門的すぎず、適度にわかりやすく

【トーン】
- 実装の経験を共有する姿勢
- 読者に有益な情報を提供
- 謙虚で共感を呼ぶ表現
- 技術コミュニティへの貢献意識

以下の形式で出力してください：

TITLE: [タイトルをここに]

CONTENT:
[本文をここに（マークダウン形式）]

この形式を厳守してください。"""

    try:
        # API呼び出し
        response = model.generate_content(prompt)
        generated_text = response.text.strip()

        # タイトルと本文を分離
        if "TITLE:" in generated_text and "CONTENT:" in generated_text:
            parts = generated_text.split("CONTENT:", 1)
            title_part = parts[0].replace("TITLE:", "").strip()
            content_part = parts[1].strip()

            return {
                'title': title_part,
                'content': content_part
            }
        else:
            # フォーマットが正しくない場合のフォールバック
            lines = generated_text.split('\n')
            title = lines[0].strip() if lines else "タイトルなし"
            content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else generated_text

            return {
                'title': title,
                'content': content
            }

    except Exception as e:
        raise Exception(f"Note記事の生成に失敗しました: {str(e)}")


def main():
    """コマンドラインインターフェース"""
    import argparse

    parser = argparse.ArgumentParser(
        description='活動内容からNote記事を生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python generate_note.py "今日はPythonでAPIを実装しました"
  python generate_note.py "新しいプロジェクト開始" --style casual
  python generate_note.py "初心者向けチュートリアル" --style tutorial
        """
    )

    parser.add_argument(
        'content',
        help='活動内容'
    )

    parser.add_argument(
        '--style',
        choices=['technical', 'casual', 'tutorial'],
        default='technical',
        help='記事のスタイル（デフォルト: technical）'
    )

    args = parser.parse_args()

    try:
        print(f"🤖 Gemini APIでNote記事を生成中...")
        print(f"📝 活動内容: {args.content}")
        print(f"🎨 スタイル: {args.style}")
        print()

        # 記事生成
        article = generate_note_article(args.content, args.style)

        # 結果表示
        print("=" * 80)
        print("✅ Note記事が生成されました")
        print("=" * 80)
        print()
        print(f"【タイトル】")
        print(article['title'])
        print()
        print("=" * 80)
        print(f"【本文】")
        print("=" * 80)
        print(article['content'])
        print()
        print("=" * 80)
        print(f"📊 タイトル文字数: {len(article['title'])}")
        print(f"📊 本文文字数: {len(article['content'])}")
        print()

    except ValueError as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
