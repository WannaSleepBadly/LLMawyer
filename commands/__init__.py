from .start import start_command
from .status import status_command

"""
Модуль логики за командами бота
"""

# TODO добавить команду /punct с указанием конкретного пункта закона
# TODO добавить команду /explain с объяснением, что регулирует конкретный ФЗ, на какие вопросы отвечает
__all__ = ['start_command', 'status_command']
