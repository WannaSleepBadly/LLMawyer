# Обработчики сообщений
from .voice import handle_voice
from .text import handle_text
from .other import handle_other
from .buttons import button_callback

__all__ = ['handle_voice', 'handle_text', 'handle_other', 'button_callback']
