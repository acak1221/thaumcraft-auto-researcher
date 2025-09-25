from PIL import Image
import onnxruntime as ort
import logging

from src.utils import constants
from src.utils.performance import timeit
from src.logic.onnx_inference import OnnxObjectDetection, ObjectPrediction
from src.logic import digit_recognition


class _NeurolinkClass:
    field_aspects_model: OnnxObjectDetection
    inventory_aspects_model: OnnxObjectDetection

    def __init__(self):
        # Detect available ORT providers and intersect with desired ones
        available_providers = ort.get_available_providers()
        desired_providers = [p for p in constants.ORT_PROVIDERS if p in available_providers]
        selected_providers = desired_providers or list(available_providers)
        
        logging.info(f"Initializing Neurolink with providers: {selected_providers}")

        try:
            with open(constants.FIELD_CLASS_NAMES_PATH) as file:
                self.field_aspects_model = OnnxObjectDetection(
                    model_path=constants.FIELD_OBJECT_DETECTION_PATH,
                    class_names=file.read().strip().split(),
                    img_size=constants.DETECTION_IMG_SIZE,
                    providers=selected_providers,
                    intra_op_num_threads=constants.ORT_INTRA_OP_THREADS,
                    inter_op_num_threads=constants.ORT_INTER_OP_THREADS,
                    graph_optimization_level=constants.ORT_GRAPH_OPT_LEVEL,
                    confidence=constants.DETECTION_CONFIDENCE,
                    iou_threshold=constants.DETECTION_IOU,
                    max_detections=constants.DETECTION_MAX_DETECTIONS,
                )
            logging.info("Field aspects model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load field aspects model: {e}")
            raise RuntimeError(f"Cannot initialize field detection model: {e}")

        try:
            with open(constants.INVENTORY_CLASS_NAMES_PATH) as file:
                self.inventory_aspects_model = OnnxObjectDetection(
                    model_path=constants.INVENTORY_OBJECT_DETECTION_PATH,
                    class_names=file.read().strip().split(),
                    img_size=constants.DETECTION_IMG_SIZE,
                    providers=selected_providers,
                    intra_op_num_threads=constants.ORT_INTRA_OP_THREADS,
                    inter_op_num_threads=constants.ORT_INTER_OP_THREADS,
                    graph_optimization_level=constants.ORT_GRAPH_OPT_LEVEL,
                    confidence=constants.DETECTION_CONFIDENCE,
                    iou_threshold=constants.DETECTION_IOU,
                    max_detections=constants.DETECTION_MAX_DETECTIONS,
                )
            logging.info("Inventory aspects model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load inventory aspects model: {e}")
            raise RuntimeError(f"Cannot initialize inventory detection model: {e}")

    @timeit
    def predict_field_aspects(self, image: Image.Image) -> list[ObjectPrediction]:
        """Находит расположение аспектов на изображении рабочей зоны"""
        return self.field_aspects_model.predict(image)

    @timeit
    def predict_inventory_aspects(self, image: Image.Image) -> list[ObjectPrediction]:
        """Находит расположение аспектов на изображении инвентаря"""
        return self.inventory_aspects_model.predict(image)

    @timeit
    def predict_inventory_aspects_count(self, image: Image.Image) -> dict[str, int]:
        """
        По изображению инвентаря определяет количество аспектов.
        Возвращает словарь "Название аспекта - Его количество"
        """
        predictions = self.inventory_aspects_model.predict(image)
        return digit_recognition.aspects_count(predictions)


Neurolink = _NeurolinkClass()
