import numpy as np

from tdt.evaluation.metrics import confusion_matrix, per_class_dice, per_class_iou


def test_confusion_metrics_are_computed():
    y_true = np.array([[0, 1], [1, 2]])
    y_pred = np.array([[0, 1], [2, 2]])

    matrix = confusion_matrix(y_true, y_pred, num_classes=3)

    assert matrix.shape == (3, 3)
    assert per_class_iou(matrix)[0] == 1.0
    assert per_class_dice(matrix)[0] == 1.0
