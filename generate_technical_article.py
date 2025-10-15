#!/usr/bin/env python3
"""
技術記事生成モジュール（Qiita/Zenn用）
Gemini APIを使用して、活動内容から技術記事を生成
"""

import os
import sys
import io
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import google.generativeai as genai

# Windows環境でのUTF-8対応
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトルートのパスを追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数読み込み
load_dotenv()


def generate_technical_article(activity_content: str) -> Dict[str, str]:
    """
    活動内容から技術記事を生成（Qiita/Zenn向け）

    Args:
        activity_content: 活動内容

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

    # プロンプト作成
    prompt = f"""以下の【活動内容】をもとに、2000〜4000文字程度の技術記事を作成してください。
読者が実際に実装できるレベルの具体性を重視し、マークダウン形式で出力してください。

### 出力要件
1. 長さ
- 2000〜4000文字程度

2. 構成（必須セクション）
- はじめに：記事の概要や狙い
- 実装内容：何を実装したのか、概要を説明
- 実装の詳細：環境設定、手順、コードブロックを含めて具体的に記述
- 苦労した点・学び：開発中に直面した課題や気づき
- 今後の展望：改善案や応用可能性
- まとめ：記事全体の振り返りとメッセージ

3. 記事スタイル（後から調整可能にするため、まずは中立的に）
- 読みやすさを重視
- 技術用語は正確に、コードは必ずコードブロック形式で記載
- ストーリー性も多少残す

---

【活動内容】
{activity_content}


上記のベース記事を、QiitaやZennに最適化してください。

### 調整方針
- technical/tutorial寄りに修正
- 文体は客観的かつ簡潔に（ですます調よりも常体ベース）
- 背景やストーリーよりも「手順」「コード」「再現性」を優先
- 見出しやコード例は明確に整理
- SEOを意識してキーワード（技術名・バージョン）を多めに残す

### 出力フォーマット
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
        raise Exception(f"技術記事の生成に失敗しました: {str(e)}")


def main():
    """コマンドラインインターフェース"""
    import argparse

    parser = argparse.ArgumentParser(
        description='活動内容から技術記事を生成（Qiita/Zenn向け）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python generate_technical_article.py "今日はPythonでAPIを実装しました"
  python generate_technical_article.py "新しいプロジェクト開始"
        """
    )

    parser.add_argument(
        'content',
        help='活動内容'
    )

    args = parser.parse_args()

    try:
        print(f"🤖 Gemini APIで技術記事を生成中...")
        print(f"📝 活動内容: {args.content}")
        print()

        # 記事生成
        article = generate_technical_article(args.content)

        # 結果表示
        print("=" * 80)
        print("✅ 技術記事が生成されました（Qiita/Zenn向け）")
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
