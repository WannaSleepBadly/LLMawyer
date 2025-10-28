# ML модуль для обработки ответов и транскрипции
from .whisper_transcriber import get_transcriber, WhisperTranscriber
from .text_processor import text_processor, TextProcessor
from .cuda_manager import cuda_manager, CUDAManager

__all__ = [
    'WhisperTranscriber','TextProcessor', 'CUDAManager',
    'cuda_manager', 'text_processor', 'get_transcriber'
]