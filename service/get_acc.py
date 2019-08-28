import json
import copy
from v_rule_based_information_extraction.RbIE.service.handle import Handle

def get_annotated_json(filename):

    json_path = './PHOTOS_test_acc/json/'

    key_value_list = []
    with open(json_path + filename + '.json', 'r') as f:
        data = json.load(f)
    items = data['single'][0]['res']['items']
    for sub_item in items:
        attr = sub_item.keys()
        attr = str(attr)[12:-3]
        if attr.find('keyword') == 0 and attr.find('keyword') + 8 <= len(attr):
            key_value_list.append(sub_item)
        if attr.find('value') == 0 and attr.find('value') + 6 <= len(attr):
            key_value_list.append(sub_item)

    return key_value_list

def key_no_extract(key_value_list, item_boxes):
    for item in key_value_list:
        attr = item.keys()
        attr = str(attr)[12:-3]
        sub_dict = item[attr]
        if IOU(sub_dict['locations'][0], item_boxes) > 0.7:
            if attr[0] == 'k':
                key_id = attr[7:]
                return key_id
            if attr[0] == 'v':
                key_id = attr[5:]
                return key_id

def get_all_box(key_value_list, keyid):
    boxes = []
    for item in key_value_list:
        attr = item.keys()
        attr = str(attr)[12:-3]
        if attr[0] == 'k':
            if keyid == attr[7:]:
                boxes.append(item['keyword' + keyid]['locations'])
        else:
            if keyid == attr[5:]:
                boxes.append(item['value' + keyid]['locations'])
    return boxes

def get_acc(boxes, item_boxes, key_box):
    item_boxes_copy = copy.copy(item_boxes)
    key_box = key_box.tolist()

    if key_box not in item_boxes_copy:
        item_boxes_copy.append(key_box)

    len_annotation = len(boxes)
    len_rbie = len(item_boxes_copy)

    if len_annotation != len_rbie:
        return 0

    correct = 0
    for anno_item in boxes:
        for rbie_item in item_boxes_copy:
            if IOU(anno_item, rbie_item) > 0.7:
                correct += 1
                break
                
    if correct == len(boxes):
        return 1
    else:
        return 0

def get_annotated_box_num(key_value_list):
    max_num = 0
    for item in key_value_list:
        attr = item.keys()
        attr = str(attr)[12:-3]
        if attr[0] == 'k':
            if int(attr[7:]) > max_num:
                max_num = int(attr[7:])
        else:
            if int(attr[5:]) > max_num:
                max_num = int(attr[5:])
    return max_num
                
def IOU(bbox_a, bbox_b):
    cx1 = bbox_a[0][0]
    cy1 = bbox_a[0][1]
    cx2 = bbox_a[2][0]
    cy2 = bbox_a[2][1]

    gx1 = bbox_b[0][0]
    gy1 = bbox_b[0][1]
    gx2 = bbox_b[2][0]
    gy2 = bbox_b[2][1]

    x1 = max(cx1, gx1)
    y1 = max(cy1, gy1)
    x2 = min(cx2, gx2)
    y2 = min(cy2, gy2)

    width = x2 - x1
    height = y2 - y1

    width1 = cx2 - cx1
    height1 = cy2 - cy1

    width2 = gx2 - gx1
    height2 = gy2 - gy1

    if width <= 0 or height <= 0:
        ratio = 0
    else:
        Area = width * height
        Area1 = width1 * height1
        Area2 = width2 * height2
        ratio = Area * 1. / (Area1 + Area2 - Area)
    return ratio
