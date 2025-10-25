# ML модуль для обработки ответов и транскрипции
from .whisper_transcriber import transcriber, WhisperTranscriber
from .text_processor import text_processor, TextProcessor
from .cuda_manager import cuda_manager, CUDAManager

__all__ = [
    'get_voice_response', 'get_text_response', 'VOICE_RESPONSES', 'TEXT_RESPONSES',
    'transcriber', 'WhisperTranscriber', 'text_processor', 'TextProcessor',
    'cuda_manager', 'CUDAManager'
]
