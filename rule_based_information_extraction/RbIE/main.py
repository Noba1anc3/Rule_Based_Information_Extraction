
import cv2
import copy
import json
import random
import numpy as np

from logzero import logger
from v_rule_based_information_extraction.RbIE.service.sort_box import sort_box_by_row
from v_rule_based_information_extraction.RbIE.service.handle import Handle

class Info_Extraction():

    def __init__(self):
        self.handle = Handle(None)

    def info_extract(self, image, reco_result, key_or_not, recos_list, boxes_list):
        keys = []
        values = []
        locations = []

        invalid_keys = []
        valid_key_num = 0

        for key in self.handle.final_result_idxs:
            v_del = True
            h_del = True
            total_optimize = False
            v_del_gap = 2

            item_recos, item_boxes = self.handle.get_recos_boxes(key)

            self.handle.single_clean_process(item_recos, item_boxes)

            if key.lower().find('total') >= 0 or key.lower().find('ttl') >= 0:
                v_del = False
                h_del = False
                total_optimize = True

            if key.find(':. )') >= 0:         # LR_KEY_NEIGHBOR = TRUE   VALUE_ONLY_ONE = TRUE
                key = key[:key.find(':. )')]
                v_del_gap = 3

            self.handle.key_in_value_del(item_recos, item_boxes, reco_result, key_or_not)

            if v_del:
                self.handle.vertical_del(item_recos, item_boxes, v_del_gap)

            if h_del:
                self.handle.horizontal_del(item_recos, item_boxes)

            page_or_not, key = self.handle.page_optimize(key, item_recos, item_boxes)

            if not page_or_not:
                self.handle.without_value_key_deletion(item_recos, item_boxes, reco_result, key_or_not)

            if not page_or_not:
                key = self.handle.with_value_key_deletion(key, item_recos)

            if total_optimize:
                key = self.handle.total_optimize(key, item_recos)

            key = self.handle.key_equals_to_value(key, item_recos, item_boxes)

            key = self.handle.colon_point_space_bracket_deletion(key, item_recos)

            self.handle.single_clean_process(item_recos, item_boxes)

            if self.handle.from_to_er_ee_address_del(key, item_recos) or len(item_recos) == 0 or item_recos[0] == '':
                invalid_keys.append(key)
                continue

            keys.append(key)
            values.append(item_recos)
            locations.append(item_boxes)
            valid_key_num += 1

            logger.info("Keyword: {}".format(key))
            for item in item_recos:
                logger.info("  Value: {}".format(item))
            logger.info("\n")

            self.handle.del_aggregation_boxes(recos_list, boxes_list, item_boxes)
            self.show(image, key, item_boxes)
            cv2.waitKey(1)

        boxes_list = self.handle.boxes_to_list(boxes_list)

        for item in recos_list:
            keys.append('Aggregation')
            values.append(item)
            valid_key_num += 1
            logger.info("Keyword: {}".format('Aggregation'))
            for sub_item in item:
                logger.info("  Value: {}".format(sub_item))
            logger.info("\n")
        for item in boxes_list:
            locations.append(item)
            image = self.show(image, 'Aggregation', item)
            cv2.waitKey(1)

        logger.info("   Valid Keywords: {}".format(valid_key_num))
        logger.info(" Invalid Keywords: {}".format(len(invalid_keys)))
        for item in invalid_keys:
            logger.info("Invalid Keywords: {}".format(item))
        logger.info("\n\n")

        return keys, values, locations, image

    def show(self, image, key, item_boxes):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        boxes = np.array(item_boxes)

        cv2.drawContours(image, boxes, -1, (r, g, b), 3)
        centx = int(np.max(boxes[:, :, 0]))
        centy = int(np.min(boxes[:, :, 1]))
        image = cv2.putText(image, key, (centx, centy), cv2.FONT_HERSHEY_SIMPLEX, 1, (r, g, b), 2)

        cv2.imshow('Info Extraction', cv2.resize(image, None, None, 0.6, 0.6))

        return image

    def run(self, image, flip_bboxes, reco_result, key_or_not, table_or_not):
        self.handle._reset_()
        self.handle.__prepare__(image, flip_bboxes, reco_result)
        self.handle.pre_process()
        self.handle.extract_key(flip_bboxes, reco_result, key_or_not, table_or_not)
        recos_list, boxes_list = self.handle.boxes_aggregation(flip_bboxes, reco_result, key_or_not, table_or_not)
        keys, values, locations, image = self.info_extract(image, reco_result, key_or_not, recos_list, boxes_list)
        ret_json = self.json_organize(keys, values, locations)
        return image, ret_json

    def json_organize(self, keys, values, locations):
        items = []
        dic = {}
        item = {}
        res = {}
        for i in range(len(keys)):
            dic["value"] = values[i]
            dic["locations"] = locations[i]
            item[keys[i]] = dic
            items.append(item)
            dic = {}
            item = {}

        res["items"] = items
        json_str = json.dumps(items)
        return json_str
