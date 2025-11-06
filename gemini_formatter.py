#!/usr/bin/env python3
"""
Gemini APIを使った投稿内容の整形モジュール

各SNSプラットフォームに適した形式に文章を整形します。
"""

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()


class GeminiFormatter:
    """Gemini APIを使った文章整形クラス"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: Gemini APIキー（Noneの場合は環境変数から取得）
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Gemini APIキーが設定されていません。\n"
                ".envファイルにGEMINI_API_KEYを設定してください。"
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def format_for_x(self, text: str) -> str:
        """
        X (Twitter) 用に文章を整形

        Args:
            text: 元の文章

        Returns:
            str: X用に整形された文章
        """
        prompt = f"""以下の文章をX (Twitter) への投稿に適した形式に整形してください。

【重要な要件】
1. 内容は一切変えない・削除しない・要約しない（元の文章をそのまま使う）
2. ChatGPT特有の記号（＊、**、###など）のみを削除
3. 絵文字は必ず残す
4. 改行を適切に配置して読みやすくする
5. 段落の区切りを分かりやすくする（空行を入れる）
6. 箇条書きは「・」または「→」で表現
7. ハッシュタグがあれば末尾に配置
8. 整形後の文章のみを出力（説明文や余計なコメントは不要）

元の文章:
{text}

整形後の文章:"""

        try:
            response = self.model.generate_content(prompt)
            formatted_text = response.text.strip()

            # 念のため280文字を超えていたら警告
            if len(formatted_text) > 280:
                print(f"⚠️  警告: X投稿が280文字を超えています（{len(formatted_text)}文字）")

            return formatted_text
        except Exception as e:
            raise Exception(f"X用整形に失敗: {e}")

    def format_for_note(self, title: str, content: str) -> dict:
        """
        Note.com 用に文章を整形

        Args:
            title: 元のタイトル
            content: 元の本文

        Returns:
            dict: {'title': str, 'content': str}
        """
        # タイトル整形
        title_prompt = f"""以下のタイトルをNote.comの記事タイトルに適した形式に整形してください。

【重要な要件】
1. 内容は変えない（元のタイトルをそのまま使う）
2. ChatGPT特有の記号（＊、#、**など）のみを削除
3. 整形後のタイトルのみを出力（説明文は不要）

元のタイトル:
{title}

整形後のタイトル:"""

        # 本文整形
        content_prompt = f"""以下の文章をNote.comの記事本文に適した形式に整形してください。

【重要な要件】
1. 内容は一切変えない・削除しない・要約しない（元の文章をそのまま使う）
2. ChatGPT特有の記号（＊、**、###など）を削除
3. 適切な見出し構造を追加（## 大見出し、### 小見出し）
4. 目次が必要な場合は冒頭に追加
5. 改行を適切に配置（段落間は空行を入れる）
6. 箇条書きは「- 」で表現
7. 読みやすく、構造化された文章に
8. 整形後の文章のみを出力（説明文や余計なコメントは不要）
9. HTMLタグは使わない（MarkdownのみOK）

元の文章:
{content}

整形後の文章:"""

        try:
            # タイトル整形
            title_response = self.model.generate_content(title_prompt)
            formatted_title = title_response.text.strip()

            # 本文整形
            content_response = self.model.generate_content(content_prompt)
            formatted_content = content_response.text.strip()

            return {
                'title': formatted_title,
                'content': formatted_content
            }
        except Exception as e:
            raise Exception(f"Note用整形に失敗: {e}")

    def generate_qiita_tags(self, title: str, content: str) -> list:
        """
        Qiita記事の内容からタグを自動生成

        Args:
            title: 記事のタイトル
            content: 記事の本文

        Returns:
            list: タグのリスト（最大5個）
        """
        prompt = f"""以下のQiita記事のタイトルと本文から、適切なタグを最大5個生成してください。

【重要な要件】
1. タグは技術的なキーワードを選択
2. Qiitaで実際に使われている一般的なタグ名を使用
3. 具体的な技術名、ツール名、言語名を優先
4. 最大5個まで
5. タグのみをカンマ区切りで出力（説明文は不要）
6. 英語のタグは小文字で統一

タイトル:
{title}

本文:
{content[:1000]}

タグ（カンマ区切りで出力）:"""

        try:
            response = self.model.generate_content(prompt)
            tags_text = response.text.strip()

            # カンマ区切りで分割してリストに変換
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]

            # 最大5個に制限
            if len(tags) > 5:
                tags = tags[:5]

            return tags
        except Exception as e:
            raise Exception(f"Qiitaタグ生成に失敗: {e}")

    def format_all(self, x_text: Optional[str] = None,
                   note_title: Optional[str] = None,
                   note_content: Optional[str] = None) -> dict:
        """
        すべての投稿内容を一括整形

        Args:
            x_text: X投稿テキスト
            note_title: Noteタイトル
            note_content: Note本文

        Returns:
            dict: {
                'x_text': str or None,
                'note_title': str or None,
                'note_content': str or None
            }
        """
        result = {
            'x_text': None,
            'note_title': None,
            'note_content': None
        }

        # X用整形
        if x_text:
            print("🤖 Gemini APIでX投稿を整形中...")
            result['x_text'] = self.format_for_x(x_text)
            print(f"   元の文字数: {len(x_text)} → 整形後: {len(result['x_text'])}")

        # Note用整形
        if note_title and note_content:
            print("🤖 Gemini APIでNote記事を整形中...")
            note_formatted = self.format_for_note(note_title, note_content)
            result['note_title'] = note_formatted['title']
            result['note_content'] = note_formatted['content']
            print(f"   タイトル文字数: {len(note_title)} → {len(result['note_title'])}")
            print(f"   本文文字数: {len(note_content)} → {len(result['note_content'])}")

        return result


def main():
    """テスト用のメイン関数"""
    import sys

    if len(sys.argv) < 2:
        print("使用例: python gemini_formatter.py <text>")
        sys.exit(1)

    text = sys.argv[1]

    try:
        formatter = GeminiFormatter()

        # X用整形のテスト
        print("=" * 80)
        print("X用整形テスト")
        print("=" * 80)
        x_formatted = formatter.format_for_x(text)
        print(x_formatted)
        print()

        # Note用整形のテスト
        print("=" * 80)
        print("Note用整形テスト")
        print("=" * 80)
        note_formatted = formatter.format_for_note("テストタイトル", text)
        print(f"タイトル: {note_formatted['title']}")
        print(f"本文:\n{note_formatted['content']}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
