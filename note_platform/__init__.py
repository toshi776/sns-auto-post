"""
Note Platform Module
Gemini APIを使った記事生成とSeleniumを使ったNote.com投稿を管理
"""

from .generate_note import generate_note_article
from .post_note import post_to_note

__all__ = ['generate_note_article', 'post_to_note']
