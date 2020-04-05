import numpy as np
from functools import cmp_to_key

def sort_box(boxes):
    """
    对文字框按从上到下从左到右排序
    :param boxes: n * 4 * 2, 待排序box列表
    :return word_rects_index: 排序后下标列表,表内元素值表示输入boxes中下标
    :return word_rects: n * 4 * 2, 排好序的box列表
    """

    def relative_position_key_row(index_a, index_b):
        box_a = boxes[index_a]
        box_b = boxes[index_b]

        left_a = np.min(box_a[:, 0])
        right_a = np.max(box_a[:, 0])
        top_a = np.min(box_a[:, 1])
        bottom_a = np.max(box_a[:, 1])

        left_b = np.min(box_b[:, 0])
        right_b = np.max(box_b[:, 0])
        top_b = np.min(box_b[:, 1])
        bottom_b = np.max(box_b[:, 1])

        window = 0
        # AB不同行,A在B上
        if (top_a + bottom_a) / 2 < top_b + window or (top_b + bottom_b) / 2 > bottom_a - window:
            return -1
        # AB不同行,A在B下
        elif (top_b + bottom_b) / 2 < top_a + window or (top_a + bottom_a) / 2 > bottom_b - window:
            return 1
        # AB同行,A在B左
        elif left_a < left_b:
            return -1
        # AB同行,A在B右
        elif left_a > left_b:
            return 1
        else:
            return 0

    boxes_index = [i for i in range(len(boxes))]
    word_rects_index = sorted(boxes_index, key=cmp_to_key(relative_position_key_row), reverse=False)
    word_rects = [boxes[i] for i in word_rects_index]
    word_rects = np.array(word_rects)
    return word_rects_index, word_rects

def box_index_in_line(boxes):
    """
    分行,注意需要boxes先排序，否则结果错误,返回的是每行的box的索引
    :param boxes: n * 4 * 2, 已排好序的box列表
    :return box_in_line: row * col_i, 按行排好序的box下标列表
    """
    box_in_line = []

    for i, box in enumerate(boxes):
        if i == 0:
            # 新建一行
            line = [i]

            top_a = np.min(box[:, 1])
            bottom_a = np.max(box[:, 1])
        else:
            top_b = np.min(box[:, 1])
            bottom_b = np.max(box[:, 1])

            if (top_a + bottom_a) / 2 < top_b or (top_b + bottom_b) / 2 > bottom_a:
                box_in_line.append(line)
                # 新建一行
                line = [i]
            else:
                line.append(i)

            top_a = top_b
            bottom_a = bottom_b

        if i == len(boxes) - 1:
            box_in_line.append(line)
    return box_in_line

def sort_box_by_row(boxes, select_boxes_idx=None):
    """
    将box按行排序,行间顺序为从上到下,行内顺序为从左到右
    :param boxes: n * 4 * 2, 所有box列表
    :param select_boxes_idx: 待排序目标box下标列表,为None表示全排序
    :return index_in_row: row * n, 排序后各行各个box对应输入boxes中的下标
    :return box_in_row: row * col_i * 4 *  2, 按行排序后的boxes
    """
    if select_boxes_idx is not None and len(select_boxes_idx) == 0:
        return [], []

    if isinstance(select_boxes_idx, list) or isinstance(select_boxes_idx, np.ndarray):
        target_boxes = [boxes[i] for i in select_boxes_idx]
    else:
        target_boxes = boxes

    boxes_index, sorted_boxes = sort_box(target_boxes)
    index_in_row = box_index_in_line(sorted_boxes)  # 分行, index_in_row中的下标对应sorted_boxes
    box_in_row = []
    # 按分行后的结果组成对应的行排序box
    for i, index in enumerate(index_in_row):
        line_box = [sorted_boxes[j] for j in index]
        box_in_row.append(line_box)

    # 将index_in_row中的下标转换为对应target_boxes
    index_in_row = [[boxes_index[i] for i in indexes] for indexes in index_in_row]

    # 将index_in_row中的下标转换为对应boxes
    if isinstance(select_boxes_idx, list) or isinstance(select_boxes_idx, np.ndarray):
        index_in_row = [[select_boxes_idx[i] for i in indexes] for indexes in index_in_row]

    return index_in_row, box_in_row
