from src.logic.onnx_inference import ObjectPrediction
from typing import List


def is_digit(prediction: ObjectPrediction) -> bool:
    return prediction.predictionName in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]


def is_aspect(prediction: ObjectPrediction) -> bool:
    return not is_digit(prediction)


def prediction_inside_prediction(pred_inner: ObjectPrediction, pred_outer: ObjectPrediction) -> bool:
    """True, если pred_inner находится внутри pred_outer"""
    x_min = pred_outer.x - pred_outer.width / 2
    x_max = pred_outer.x + pred_outer.width / 2
    y_min = pred_outer.y - pred_outer.height / 2
    y_max = pred_outer.y + pred_outer.height / 2
    return x_min <= pred_inner.x <= x_max and y_min <= pred_inner.y <= y_max


def _iou(a: ObjectPrediction, b: ObjectPrediction) -> float:
    ax1 = a.x - a.width / 2
    ay1 = a.y - a.height / 2
    ax2 = a.x + a.width / 2
    ay2 = a.y + a.height / 2
    bx1 = b.x - b.width / 2
    by1 = b.y - b.height / 2
    bx2 = b.x + b.width / 2
    by2 = b.y + b.height / 2
    inter_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    inter_h = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = inter_w * inter_h
    if inter == 0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    return inter / max(1e-6, (area_a + area_b - inter))


def remove_same_spot_predictions(digit_predictions: list[ObjectPrediction]) -> list[ObjectPrediction]:
    """
    Для случаев, когда на одну цифру приходится несколько предсказаний, расположенных примерно в одном месте.
    Убирает лишние предсказания, оставляя только самые уверенные
    """
    MIN_VALID_DIFF = (
        2.0  # Минимальная разница в координатах между предсказаниями, когда предсказания считаются для разных цифр
    )
    # NMS-like suppression by x-closeness and IoU
    preds = sorted(digit_predictions, key=lambda p: p.confidence, reverse=True)
    kept: List[ObjectPrediction] = []
    for p in preds:
        suppress = False
        for k in kept:
            if abs(p.x - k.x) < MIN_VALID_DIFF and _iou(p, k) > 0.1:
                suppress = True
                break
        if not suppress:
            kept.append(p)
    kept.sort(key=lambda pred: pred.x)
    return kept


def group_aspects_and_digits(
    predictions: list[ObjectPrediction],
) -> list[tuple[ObjectPrediction, list[ObjectPrediction]]]:
    """
    Группирует цифры по аспектам, к которым цифра относится
    Returns:
        Список пар (Предсказание аспекта, Список цифр, относящихся к этому аспекту)
    """
    result = []
    for aspect_pred in predictions:
        if not is_aspect(aspect_pred):
            continue
        aspect_digits = []
        for digit_pred in predictions:
            if not is_digit(digit_pred):
                continue
            if prediction_inside_prediction(digit_pred, aspect_pred):
                aspect_digits.append(digit_pred)
        result.append((aspect_pred, aspect_digits))
    return result


def aspects_count(predictions: list[ObjectPrediction]) -> dict[str, int]:
    """
    Каждому аспекту подставляет его распознанное количество
    """
    counts = dict()
    for aspect_pred, aspect_digits_pred in group_aspects_and_digits(predictions):
        aspect_digits_pred = remove_same_spot_predictions(aspect_digits_pred)
        aspect_digits_pred.sort(key=lambda pred: pred.x)
        number = 0
        for digit_pred in aspect_digits_pred:
            number *= 10
            number += int(digit_pred.predictionName)
        counts[aspect_pred.predictionName] = number
    return counts
