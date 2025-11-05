import logging
import torch

"""
Модуль управления ресурсами GPU и CPU
"""

logger = logging.getLogger(__name__)


class CUDAManager:
    """Менеджер для работы с CUDA"""
    
    def __init__(self):
        self.device = None
        self.device_name = None
        self.is_cuda_available = False
        self._check_cuda_availability()
    
    def _check_cuda_availability(self):
        """Проверяет доступность CUDA"""
        try:
            # Проверяем доступность CUDA
            self.is_cuda_available = torch.cuda.is_available()
            
            if self.is_cuda_available:
                # Получаем информацию о GPU
                self.device = torch.device("cuda")
                self.device_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                
                logger.info(f"✅ CUDA доступна!")
                logger.info(f"🎮 GPU: {self.device_name}")
                logger.info(f"💾 Память GPU: {gpu_memory:.1f} GB")
                logger.info(f"🔧 Устройство: {self.device}")
            else:
                self.device = torch.device("cpu")
                self.device_name = "CPU"
                logger.info("⚠️ CUDA недоступна, используется CPU")
                logger.info(f"🔧 Устройство: {self.device}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке CUDA: {e}")
            self.is_cuda_available = False
            self.device = torch.device("cpu")
            self.device_name = "CPU"
            logger.info(f"🔧 Fallback на CPU: {self.device}")
    
    def get_device(self):
        """Возвращает доступное устройство"""
        return self.device
    
    def get_device_name(self):
        """Возвращает название устройства"""
        return self.device_name
    
    def is_cuda_enabled(self):
        """Возвращает True если CUDA доступна"""
        return self.is_cuda_available
    
    def get_device_info(self):
        """Возвращает информацию об устройстве"""
        if self.is_cuda_available:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return {
                "device": str(self.device),
                "name": self.device_name,
                "memory_gb": round(gpu_memory, 1),
                "is_cuda": True
            }
        else:
            return {
                "device": str(self.device),
                "name": self.device_name,
                "memory_gb": None,
                "is_cuda": False
            }


# Глобальный экземпляр менеджера CUDA
cuda_manager = CUDAManager()
