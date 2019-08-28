import re
import copy
import numpy as np
from v_dar_tools.business_tool.business_logic import BusinessLogic
from v_rule_based_information_extraction.RbIE.service.sort_box import sort_box_by_row

class Handle(BusinessLogic):

    def __init__(self, business_config):
        BusinessLogic.__init__(self, business_config)

    def pre_process(self):
        pass
        # self._rectify_by_horizontal_line()
        # self._rectify_by_detection_box_angle()
        # self._enhance_image_by_gamma()

    def extract_key(self, flip_bboxes, reco_result, key_or_not, table_or_not):
        key_recos = []
        key_boxes = []
        self.final_result_idxs = {}

        image_length = self.page.image.shape[1]
        image_width = self.page.image.shape[0]
        TABLE = True

        TABLE_TOP = image_width
        for index in range(len(flip_bboxes)):
            if table_or_not[index]:
                flip_bbox = flip_bboxes[index]
                box_y_top = flip_bbox[0][1]
                if box_y_top < TABLE_TOP:
                    TABLE_TOP = box_y_top
                    
        TABLE_BOTTOM = 0
        for index in range(len(flip_bboxes)):
            if table_or_not[index]:
                flip_bbox = flip_bboxes[index]
                box_y_bottom = flip_bbox[3][1]
                if box_y_bottom > TABLE_BOTTOM:
                    TABLE_BOTTOM = box_y_bottom

        if TABLE_BOTTOM == 0:
            TABLE = False

        index_list_temp, sorted_list_temp = sort_box_by_row(flip_bboxes)
        index_list = []

        list = []
        index_list_len = len(index_list_temp)
        for index_1 in range(index_list_len):
            sub_list = index_list_temp[index_1]
            sub_list_len = len(sub_list)
            for index_2 in range(sub_list_len):
                list.append(sub_list[index_2])
            index_list.append(list)
            list = []

        for box_index in range(len(key_or_not)):
            KON = key_or_not[box_index]
            TON = table_or_not[box_index]

            R_FOUND = False
            B_FOUND = False
            
            LR_KEY_NEIGHBOR = False
            VALUE_ONLY_ONE = False

            if KON and not TON:
                box = flip_bboxes[box_index]
                rec = reco_result[box_index]

                box1_left = box[0][0]
                box1_right = box[1][0]

                left = box[0][0]
                top = box[0][1]
                right = box[2][0]
                bottom = box[2][1]

                break_lock = 0
                for row_index in range(len(index_list)):
                    sub_list = index_list[row_index]
                    for col_index in range(len(sub_list)):
                        item = sub_list[col_index]
                        if item == box_index:
                            if (col_index == 0 and (len(sub_list) == 1 or key_or_not[sub_list[1]]))\
                                or (col_index + 1 == len(sub_list) and key_or_not[sub_list[col_index - 1]])\
                                or (key_or_not[sub_list[col_index - 1]] and key_or_not[sub_list[col_index + 1]]):
                                    LR_KEY_NEIGHBOR = True
                            if len(sub_list) > col_index + 1:
                                for iter_index in range(col_index + 1, len(sub_list)):
                                    if key_or_not[sub_list[iter_index]] == 1:
                                        right = flip_bboxes[sub_list[iter_index]][0][0]
                                        break_lock = True
                                        R_FOUND = True
                                        break
                                if break_lock:
                                    break
                                else:
                                    if image_width < image_length:
                                        if left < image_length / 3:
                                            right = int(image_length / 2)
                                        elif left < image_length / 2:
                                            right = int(image_length * 2 / 3)
                                        else:
                                            right = image_length
                                    else:
                                        if left < image_length * 0.3:
                                            right = int(image_length / 2)
                                        else:
                                            right = image_length

                                    FIRST_R_BOX = flip_bboxes[sub_list[col_index + 1]]
                                    FR_BOX_XMID = (FIRST_R_BOX[0][0] + FIRST_R_BOX[1][0]) / 2
                                    if FR_BOX_XMID < right:
                                        FR_BOX_XLEFT = FIRST_R_BOX[0][0]
                                        FR_BOX_YTOP = FIRST_R_BOX[1][1]
                                        FR_BOX_YBOTTOM = FIRST_R_BOX[2][1]
                                        FR_BOX_HEIGHT = FR_BOX_YBOTTOM - FR_BOX_YTOP
                                        for index in range(len(flip_bboxes)):
                                            flip_bbox = flip_bboxes[index]
                                            bbox_xlft = flip_bbox[0][0]
                                            bbox_ytop = flip_bbox[0][1]
                                            x_diff = FR_BOX_XLEFT - bbox_xlft
                                            y_diff = FR_BOX_YTOP - bbox_ytop
                                            if x_diff < 0:
                                                x_diff = -1 * x_diff
                                            if y_diff < 0:
                                                y_diff = -1 * y_diff
                                            if x_diff < 22 and y_diff < 2.2 * FR_BOX_HEIGHT and key_or_not[index] == 1:
                                                right = flip_bboxes[sub_list[col_index]][1][0]
                                                break
                                    break_lock = True
                                    break
                            else:
                                if image_width < image_length:
                                    if left < image_length / 3:
                                        right = int(image_length / 2)
                                    elif left < image_length / 2:
                                        right = int(image_length * 2 / 3)
                                    else:
                                        right = image_length
                                else:
                                    if left < image_length * 0.3:
                                        right = int(image_length / 2)
                                    else:
                                        right = image_length
                                break_lock = True
                                break
                    if break_lock:
                        break_lock = False
                        break

                break_lock = False
                if row_index < len(index_list):
                    for row_index_iter in range(row_index + 1, len(index_list)):
                        row = index_list[row_index_iter]
                        for item in row:
                            if table_or_not[item] == 1:
                                bottom = flip_bboxes[item][0][1]
                                break_lock = True
                                break
                            else:
                                if key_or_not[item] == 1:
                                    box2_left = flip_bboxes[item][0][0]
                                    box2_right = flip_bboxes[item][1][0]
                                    overlap = self.overlap(box1_left, box1_right, box2_left, box2_right)
                                    if overlap > 0.2:
                                        bottom = flip_bboxes[item][0][1]
                                        break_lock = True
                                        B_FOUND = True
                                        break
                                else:
                                    if top < image_width * 0.4:
                                        bottom = int(image_width / 2)
                                    else:
                                        bottom = image_width
                        if break_lock:
                            break_lock = False
                            break
                else:
                    bottom = image_width

                lower_rec = rec.lower()
                if lower_rec.find('total') >= 0 or lower_rec.find('ttl') >= 0:
                    TOTAL_Y_MID = (box[1][1] + box[2][1]) / 2
                    NUM_IN_VERTICAL = 0
                    NUM_IN_HORIZONTAL = 0

                    PASS  = False
                    R_KEY = False
                    D_KEY = False
                    COLON = False
                    H_PREFER = False
                    V_PREFER = False
                    GET_TABLE_HEAD = True

                    right_1 = image_length
                    bottom_1 = box[2][1]
                    right_2 = box[2][0]
                    bottom_2 = image_width

                    if TABLE:
                        if TOTAL_Y_MID < TABLE_TOP:
                            bottom_2 = TABLE_TOP
                            GET_TABLE_HEAD = False
                        elif TOTAL_Y_MID > TABLE_BOTTOM:
                            pass
                        else:
                            bottom_2 = TABLE_BOTTOM

                    if R_FOUND:
                        right_1 = right
                    if B_FOUND:
                        bottom_2 = bottom

                    rect_horizontal = [[left, top], [right_1, bottom_1]]
                    rect_vertical = [[left, top], [right_2, bottom_2]]
                    box_in_horizontal = self.page.box_in_rect(rect_horizontal)
                    box_in_vertical = self.page.box_in_rect(rect_vertical)

                    if rec.find(':') >= 0:
                        COLON = True
                        rec = rec[:rec.find(':')]

                    for item in box_in_vertical:
                        if key_or_not[item] == 0 and reco_result[item].lower().find('total') < 0:
                            lower_str = reco_result[item].lower()
                            for index in range(len(reco_result[item])):
                                bit = reco_result[item][index]
                                if bit.isdigit() or bit == '.' or bit == ',' or bit == ' ':
                                    PASS = True
                                elif lower_str.find('kg') >= 0:
                                    if index == lower_str.find('kg') or index == lower_str.find('kg') + 1:
                                        PASS = True
                                    else:
                                        PASS = False
                                elif lower_str.find('usd') >= 0:
                                    if index == lower_str.find('usd') or index == lower_str.find('usd') + 1 or index == lower_str.find('usd') + 2:
                                        PASS = True
                                    else:
                                        PASS = False
                                else:
                                    PASS = False
                                    break
                            if PASS:
                                NUM_IN_VERTICAL += 1

                    for item in box_in_horizontal:
                        if key_or_not[item] == 0 and reco_result[item].lower().find('total') < 0:
                            lower_str = reco_result[item].lower()
                            for bit in reco_result[item]:
                                if bit.isdigit() or bit == '.' or bit == ',' or bit == ' ' or lower_str.find('kg') >= 0:
                                    PASS = True
                                else:
                                    PASS = False
                                    break
                            if PASS:
                                NUM_IN_HORIZONTAL += 1

                    Y_TOP = image_width
                    Y_TOP_INDEX = len(flip_bboxes) - 1
                    for item in box_in_vertical:
                        vbox = flip_bboxes[item]
                        if not self.IOU(box, vbox):
                            y_top = vbox[0][1]
                            if y_top < Y_TOP:
                                Y_TOP = y_top
                                Y_TOP_INDEX = item

                    X_LFT = image_length
                    X_LFT_INDEX = len(flip_bboxes) - 1
                    for item in box_in_horizontal:
                        hbox = flip_bboxes[item]
                        if not self.IOU(box, hbox):
                            x_lft = hbox[0][0]
                            if x_lft < X_LFT:
                                X_LFT = x_lft
                                X_LFT_INDEX = item

                    if key_or_not[Y_TOP_INDEX]:
                        H_PREFER = True
                    if key_or_not[X_LFT_INDEX]:
                        V_PREFER = True

                    if not len(box_in_horizontal):
                        box_in_idx = box_in_vertical
                    if not len(box_in_vertical):
                        box_in_idx = box_in_horizontal

                    if len(box_in_horizontal) and len(box_in_vertical):

                        if NUM_IN_HORIZONTAL >= NUM_IN_VERTICAL:
                            box_in_idx = box_in_horizontal
                        else:
                            box_in_idx = box_in_vertical

                        if V_PREFER:
                            box_in_idx = box_in_vertical
                        if H_PREFER or COLON:
                            box_in_idx = box_in_horizontal

                    for item in box_in_idx:

                        table_head = ''

                        if GET_TABLE_HEAD:
                            item_box = flip_bboxes[item]
                            item_box_x_left = item_box[0][0]
                            item_box_x_right = item_box[1][0]

                            for index in range(len(flip_bboxes)):
                                if key_or_not[index] and table_or_not[index]:
                                    kt_box = flip_bboxes[index]
                                    kt_box_x_left = kt_box[0][0]
                                    kt_box_x_right = kt_box[1][0]
                                    overlap = self.overlap(item_box_x_left, item_box_x_right, kt_box_x_left, kt_box_x_right)
                                    if overlap > 0.4:
                                        table_head += reco_result[index] + ' '

                            if not table_head == '':
                                table_head = ' (' + table_head.strip() + ')'

                        rec_new = rec + table_head

                        for key_item in key_recos:
                            if key_item == rec_new:
                                rec_new += ' '
                        key_recos.append(rec_new)
                        key_boxes.append(box)

                        self.final_result_idxs[rec_new] = [item]

                else:
                    rect = [[left, top], [right, bottom]]
                    box_in_idx = self.page.box_in_rect(rect)
                    
                    if len(box_in_idx) == 2:
                        VALUE_ONLY_ONE = True
                    
                    if LR_KEY_NEIGHBOR and VALUE_ONLY_ONE and rec.find(':') < 0:
                        rec += ':. )'
                        
                    for key_item in key_recos:
                        if key_item == rec:
                            rec += ' '
                    key_recos.append(rec)
                    key_boxes.append(box)
                    
                    self.final_result_idxs[rec] = box_in_idx

    def boxes_aggregation(self, flip_bboxes, reco_result, key_or_not, table_or_not):
        agg_list = []
        image_width = self.page.image.shape[0]
        image_length = self.page.image.shape[1]

        for index in range(len(flip_bboxes)):
            if not key_or_not[index] and not table_or_not[index]:

                # IF CURRENT INDEX->BOX HAVE BEEN APPENDED INTO A AGG_BLOCK(BOXES) IN AGG_LIST(BLOCKES)
                # DO NOT HANDLE ON IT (CONTINUE)
                break_sign = False
                continue_sign = False
                if not len(agg_list) == 0:
                    for sub_agg_list in agg_list:
                        for item in sub_agg_list:
                            if index == item:
                                continue_sign = True
                                break_sign = True
                                break
                        if break_sign:
                            break
                if continue_sign:
                    continue

                box_y_bottom = flip_bboxes[index][2][1]
                box_x_left = flip_bboxes[index][0][0]
                box_x_right = flip_bboxes[index][1][0]
                box_length = box_x_right - box_x_left

                # ONLY HANDLE ON THE BOX WHICH LENGTH IS LESS THAN HALF OF IMG_LENGTH
                # AND IT'S BOTTOM IS UPPER THAN HALF OF IMG_WIDTH
                if 2 * box_y_bottom < image_width and 2 * box_length < image_length:
                    box_y_top = flip_bboxes[index][1][1]
                    boxes_upper_top = box_y_top
                    boxes_lower_top = box_y_top
                    box_height = box_y_bottom - box_y_top
                    kv_index_list = [index]
                    kv_x_list = [box_x_left]
                    kv_h_list = [box_height]

                    # AFFILIATED_LIST COMPRISES OF ALL THE BRO_BOXES BELONG TO MAIN_BOX IN CURRENT ROW
                    AFFILIATED_LIST = []
                    ROW_X_RIGHT = box_x_right

                    # FOR: FIND A NEAREST BROTHER BOX
                    # WHILE TRUE: APPEND IT INTO AFFILIATED_LIST
                    while True:
                        MINIMUM_ROW_X_IDX = -1
                        MINIMUM_ROW_X_LFT = image_length
                        for index_row in range(len(flip_bboxes)):
                            if not key_or_not[index_row] and not table_or_not[index_row]:
                                row_box_x_left = flip_bboxes[index_row][0][0]
                                row_box_y_top = flip_bboxes[index_row][0][1]
                                y_diff = row_box_y_top - box_y_top
                                if -9 < y_diff and y_diff < 9:
                                    if row_box_x_left < MINIMUM_ROW_X_LFT and row_box_x_left > ROW_X_RIGHT and row_box_x_left < ROW_X_RIGHT + 100:
                                        MINIMUM_ROW_X_LFT = row_box_x_left
                                        MINIMUM_ROW_X_IDX = index_row
                        # FIND A NEAREST BRO_BOX
                        if not MINIMUM_ROW_X_IDX == -1:
                            ROW_X_RIGHT = flip_bboxes[MINIMUM_ROW_X_IDX][1][0]
                            AFFILIATED_LIST.append(MINIMUM_ROW_X_IDX)
                        else:
                            break


                    cycle_times = 0
                    while True:
                        kv_index_before = copy.copy(kv_index_list)
                        for val_index in range(len(flip_bboxes)):
                            if not key_or_not[val_index] and not table_or_not[val_index] and val_index not in kv_index_list:
                                val_box_y_bottom = flip_bboxes[val_index][2][1]
                                val_box_x_left = flip_bboxes[val_index][0][0]
                                val_box_x_right = flip_bboxes[val_index][1][0]
                                val_box_length = val_box_x_right - val_box_x_left
                                if 2 * val_box_y_bottom < image_width and 2 * val_box_length < image_length:
                                    val_box_y_top = flip_bboxes[val_index][1][1]
                                    val_box_height = val_box_y_bottom - val_box_y_top
                                    x_diff = val_box_x_left - self.get_average(kv_x_list)
                                    if -20 < x_diff and x_diff < 20:
                                        if self.get_average(kv_h_list) * 3 / 4 < val_box_height < self.get_average(kv_h_list) * 5 / 4:
                                            delta_upper_top = boxes_upper_top - val_box_y_top
                                            delta_lower_top = val_box_y_top - boxes_lower_top

                                            if delta_lower_top > 0 and delta_lower_top < 1.5 * self.get_average(kv_h_list):
                                                boxes_lower_top = val_box_y_top
                                                kv_index_list.append(val_index)
                                                kv_x_list.append(val_box_x_left)
                                                kv_h_list.append(val_box_height)

                                                # FIND BRO_BOXES FOR CURRENT MAIN_BOX
                                                ROW_X_RIGHT = val_box_x_right
                                                while True:
                                                    MINIMUM_ROW_X_IDX = -1
                                                    MINIMUM_ROW_X_LFT = image_length
                                                    for index_row in range(len(flip_bboxes)):
                                                        if not key_or_not[index_row] and not table_or_not[index_row]:
                                                            row_box_x_left = flip_bboxes[index_row][0][0]
                                                            row_box_y_top = flip_bboxes[index_row][0][1]
                                                            y_diff = row_box_y_top - val_box_y_top
                                                            if -9 < y_diff and y_diff < 9:
                                                                if row_box_x_left < MINIMUM_ROW_X_LFT and row_box_x_left > ROW_X_RIGHT and row_box_x_left < ROW_X_RIGHT + 100:
                                                                    MINIMUM_ROW_X_LFT = row_box_x_left
                                                                    MINIMUM_ROW_X_IDX = index_row
                                                    if not MINIMUM_ROW_X_IDX == -1:
                                                        ROW_X_RIGHT = flip_bboxes[MINIMUM_ROW_X_IDX][1][0]
                                                        AFFILIATED_LIST.append(MINIMUM_ROW_X_IDX)
                                                    else:
                                                        break

                                                break

                                            if delta_upper_top > 0 and delta_upper_top < 1.5 * self.get_average(kv_h_list):
                                                boxes_upper_top = val_box_y_top
                                                kv_index_list.append(val_index)
                                                kv_x_list.append(val_box_x_left)
                                                kv_h_list.append(val_box_height)

                                                # FIND BRO_BOXES FOR CURRENT MAIN_BOX
                                                ROW_X_RIGHT = val_box_x_right
                                                while True:
                                                    MINIMUM_ROW_X_IDX = -1
                                                    MINIMUM_ROW_X_LFT = image_length
                                                    for index_row in range(len(flip_bboxes)):
                                                        if not key_or_not[index_row] and not table_or_not[index_row]:
                                                            row_box_x_left = flip_bboxes[index_row][0][0]
                                                            row_box_y_top = flip_bboxes[index_row][0][1]
                                                            y_diff = row_box_y_top - val_box_y_top
                                                            if -9 < y_diff and y_diff < 9:
                                                                if row_box_x_left < MINIMUM_ROW_X_LFT and row_box_x_left > ROW_X_RIGHT and row_box_x_left < ROW_X_RIGHT + 100:
                                                                    MINIMUM_ROW_X_LFT = row_box_x_left
                                                                    MINIMUM_ROW_X_IDX = index_row
                                                    if not MINIMUM_ROW_X_IDX == -1:
                                                        ROW_X_RIGHT = flip_bboxes[MINIMUM_ROW_X_IDX][1][0]
                                                        AFFILIATED_LIST.append(MINIMUM_ROW_X_IDX)
                                                    else:
                                                        break

                                                break

                        cycle_times += 1

                        if kv_index_list == kv_index_before or cycle_times == 10:
                            break

                    # FIND MAXIMUM_X_RIGHT IN KV_INDEX_LIST
                    # FOR APPENDING AFFILIATED_ITEMS INTO KV_INDEX_LIST
                    BLOCK_MAX_X_RIGHT = 0
                    for item in kv_index_list:
                        box_x_right = flip_bboxes[item][1][0]
                        if box_x_right > BLOCK_MAX_X_RIGHT:
                            BLOCK_MAX_X_RIGHT = box_x_right

                    # ONLY KEEP 'LEN_OF_KV_INDEX_LIST' FROM FOUR TO SEVEN
                    # IF AFFILIATED_ITEM'S X_LEFT  MORE THAN  MAXIMUM_X_RIGHT IN ORIGINAL K_V_LIST
                    # DO NOT KEEP THAT ITEM
                    # OTHERWISE, APPEND IT INTO KV_INDEX_LIST (CURRENT AGGREGATION BLOCK)
                    if len(kv_index_list) > 3 and len(kv_index_list) < 8:
                        for affiliated_item in AFFILIATED_LIST:
                            affiliated_box_x_left = flip_bboxes[affiliated_item][0][0]
                            if not affiliated_box_x_left > BLOCK_MAX_X_RIGHT:
                                kv_index_list.append(affiliated_item)
                        agg_list.append(kv_index_list)

        # DEL AGGREGATION_BLOCK WHICH BELONGS TO ANOTHER 'BIGGER' AGGREGATION BLOCK
        while True:
            break_sign = False
            for index_bef in range(len(agg_list)):
                item_bef = agg_list[index_bef]
                for index_aft in range(len(agg_list)):
                    if index_aft != index_bef:
                        item_aft = agg_list[index_aft]
                        if not [False for i in item_bef if i not in item_aft]:
                            del agg_list[index_bef]
                            break_sign = True
                            break
                if break_sign:
                    break
            if not break_sign:
                break

        agg_boxes_list = []
        agg_recos_list = []

        for agg_item in agg_list:
            agg_item_boxes_temp = self.page.box_list[agg_item]
            agg_item_recos_temp = self.page.content_list[agg_item]
            index_list, sorted_list = sort_box_by_row(np.array(agg_item_boxes_temp))

            agg_flip_bboxes = []
            agg_reco_result = []
            for index in range(len(index_list)):
                item = index_list[index]
                for sub_index in range(len(item)):
                    sub_item = item[sub_index]
                    agg_flip_bboxes.append(agg_item_boxes_temp[sub_item])
                    agg_reco_result.append(agg_item_recos_temp[sub_item])

            agg_boxes_list.append(agg_flip_bboxes)
            agg_recos_list.append(agg_reco_result)

        return agg_recos_list, agg_boxes_list

    def key_in_value_del(self, item_recos, item_boxes, reco_result, key_or_not):
        try:
            if len(item_recos) > 1:
                for index in range(len(item_recos) - 1, 0, -1):
                    count = 0
                    item = item_recos[index]
                    for rr_index in range(len(reco_result)):
                        if reco_result[rr_index] == item and key_or_not[rr_index] == 1:
                            for rr_item in reco_result:
                                if item == rr_item:
                                    count += 1
                            if count == 1:
                                del item_recos[index]
                                del item_boxes[index]
                            break
        except:
            pass

    def vertical_del(self, item_recos, item_boxes, v_del_gap):
        try:
            if len(item_recos) > 1:
                for aft_index in range(len(item_recos) - 1, 0, -1):
                    pre_index = aft_index - 1
                    pre_box_up_y = item_boxes[pre_index][0][1]
                    aft_box_up_y = item_boxes[aft_index][0][1]
                    boxes_gap = aft_box_up_y - pre_box_up_y
                    height_pre = item_boxes[pre_index][3][1] - item_boxes[pre_index][0][1]
                    height_aft = item_boxes[aft_index][3][1] - item_boxes[aft_index][0][1]
                    height_avg = (height_pre + height_aft) / 2
                    if boxes_gap > height_avg * v_del_gap:
                        for index in range(len(item_recos) - 1, pre_index, -1):
                            del item_boxes[index]
                            del item_recos[index]
        except:
            pass

    def horizontal_del(self, item_recos, item_boxes):
        try:
            if len(item_recos) > 2:
                WAIT_FOR_BLOCK_X_MAX = []
                # Determine BLOCK_TYPE on X_DIRECTION
                # Type-01: |
                # Type-02: ┐
                zero_box_x_left = item_boxes[0][0][0]
                one_box_x_left  = item_boxes[1][0][0]
                two_box_x_left  = item_boxes[2][0][0]

                two_one_x_gap  = two_box_x_left - one_box_x_left
                one_zero_x_gap = one_box_x_left - zero_box_x_left

                if two_one_x_gap < 0:
                    two_one_x_gap = -1 * two_one_x_gap
                if one_zero_x_gap < 0:
                    one_zero_x_gap = -1 * one_zero_x_gap

                if one_zero_x_gap > 22 and one_zero_x_gap < 300 and two_one_x_gap < 22:
                    key_box_x_left  = one_box_x_left
                    key_box_x_mid   = (item_boxes[1][0][0] + item_boxes[1][1][0]) / 2
                    key_box_y_top   = item_boxes[1][0][1]
                    key_box_height  = item_boxes[1][2][1] - item_boxes[1][1][1]
                else:
                    key_box_x_left  = zero_box_x_left
                    key_box_x_mid   = (item_boxes[0][0][0] + item_boxes[0][1][0]) / 2
                    key_box_y_top   = item_boxes[0][0][1]
                    key_box_height  = item_boxes[0][2][1] - item_boxes[0][1][1]

                for aft_index in range(len(item_recos) - 1, 0, -1):

                    aft_box_x_left  = item_boxes[aft_index][0][0]
                    aft_box_x_right = item_boxes[aft_index][1][0]
                    aft_box_x_mid   = (aft_box_x_left + aft_box_x_right) / 2
                    aft_box_y_top   = item_boxes[aft_index][0][1]

                    y_top_diff  = aft_box_y_top - key_box_y_top
                    x_left_diff = aft_box_x_left - key_box_x_left
                    x_mid_diff  = aft_box_x_mid - key_box_x_mid

                    if y_top_diff < 0:
                        y_top_diff = -1 * y_top_diff
                    if x_left_diff < 0:
                        x_left_diff = -1 * x_left_diff
                    if x_mid_diff < 0:
                        x_mid_diff = -1 * x_mid_diff

                    if x_left_diff < 25 or y_top_diff < 9 or x_mid_diff < 50:
                        if x_left_diff > 500:
                            del item_boxes[aft_index]
                            del item_recos[aft_index]
                        else:
                            continue
                    else:
                        KEEP = False
                        BROTHER = False

                        # FIND ITS BRO_BOX
                        for bro_index in range(0, len(item_boxes)):
                            if bro_index != aft_index:
                                y_diff = item_boxes[aft_index][0][1] - item_boxes[bro_index][0][1]
                                if -8 < y_diff and y_diff < 8:
                                    bro_box_x_left = item_boxes[bro_index][0][0]
                                    x_diff = bro_box_x_left - key_box_x_left
                                    if -25 < x_diff and x_diff < 25:
                                        BROTHER = True
                                        break
                        
                        if BROTHER:
                            bro_box_height = item_boxes[bro_index][2][1] - item_boxes[bro_index][1][1]
                            aft_box_height = item_boxes[aft_index][2][1] - item_boxes[aft_index][1][1]
                            aft_bro_ratio  = aft_box_height / bro_box_height
                            if aft_bro_ratio > 5/4:
                                BROTHER = False
                            else:
                                X_BROS_MAX = item_boxes[bro_index][1][0]

                        if BROTHER:
                            # FIND ALL THE 'BRIDGE_BOXES' BETWEEN BRO_BOX AND AFT_INDEX_BOX
                            # TO UPDATE X_BROS_MAX ALONG X ——> DIRECTION
                            cycle_times = 0
                            while True:
                                x_bros_max_before = X_BROS_MAX
                                for bridge_index in range(0, len(item_boxes)):
                                    if bridge_index != bro_index and bridge_index != aft_index:
                                        bridge_x_left = item_boxes[bridge_index][0][0]
                                        bridge_x_right = item_boxes[bridge_index][1][0]

                                        y_diff = item_boxes[aft_index][0][1] - item_boxes[bridge_index][0][1]
                                        x_diff = bridge_x_left - X_BROS_MAX

                                        if y_diff < 0:
                                            y_diff = -1 * y_diff
                                        if x_diff < 0:
                                            x_diff = -1 * x_left_diff

                                        if y_diff < 9 and x_diff < 80 and bridge_x_right > X_BROS_MAX:
                                            X_BROS_MAX = bridge_x_right
                                            break

                                cycle_times += 1

                                if X_BROS_MAX == x_bros_max_before or cycle_times == 10:
                                    break

                            x_diff = item_boxes[aft_index][0][0] - X_BROS_MAX
                            if x_diff < 80:
                                KEEP = True
                            else:
                                WAIT_FOR_BLOCK_X_MAX.append(aft_index)
                        else:
                            del item_boxes[aft_index]
                            del item_recos[aft_index]

                # GET X_RIGHT_MAX ON ALL THE BOXES IN THE KEY-VALUE BLOCK AFTER HORIZONAL DELETION
                BLOCK_X_MAX = 0
                for index in range(len(item_boxes)):
                    if index not in WAIT_FOR_BLOCK_X_MAX:
                        item_box_x_right = item_boxes[index][1][0]
                        if item_box_x_right > BLOCK_X_MAX:
                            BLOCK_X_MAX = item_box_x_right

                # DEL BOX IN  LIST[WAIT_FOR_BLOCK_X_MAX]  BASED ON  BLOCK_X_MAX
                for index in range(len(WAIT_FOR_BLOCK_X_MAX) - 1, -1, -1):
                    BOX_X_RIGHT = item_boxes[index][1][0]
                    if BLOCK_X_MAX < BOX_X_RIGHT:
                        del item_recos[index]
                        del item_boxes[index]

                for aft_index in range(len(item_recos) - 1, 0, -1):
                    aft_box_height = item_boxes[aft_index][2][1] - item_boxes[aft_index][1][1]
                    x_diff = item_boxes[aft_index][0][0] - key_box_x_left
                    if aft_box_height > 1.3 * key_box_height and x_diff > 50:
                        del item_boxes[aft_index]
                        del item_recos[aft_index]
        except:
            pass

    def page_optimize(self, key, item_recos, item_boxes):
        try:
            if len(item_recos) > 0:
                key = key.strip()
                page_index = item_recos[0].lower().find('page')
                if page_index >= 0:
                    item_recos[0] = item_recos[0][page_index:]
                    key = key[key.lower().find('page'):key.lower().find('page') + 4]
                    num_list = re.findall(r"\d+\.?\d*", item_recos[0])
                    if len(num_list) > 0:
                        item_recos[0] = num_list[0]
                        if len(item_recos) > 1:
                            for index in range(len(item_recos) - 1, 0, -1):     # NOT-RELATED DELETION
                                del item_recos[index]
                                del item_boxes[index]
                    else:
                        if len(item_recos) == 1:
                            item_recos[0] = '1'        # PAGE INFORMATION NOT FOUND, DEFAULT = 1
                        elif len(item_recos) == 2:     # TWO PAGE BOXES: GO BOX-2 TO FIND PAGE INFORMATION
                            num_list = re.findall(r"\d+\.?\d*", item_recos[1])
                            if len(num_list) >= 1:
                                item_recos[1] = num_list[0]
                            else:
                                item_recos[1] = '1'
                            del item_recos[0]
                            del item_boxes[0]
                        else:                         # MANY PAGE BOXES
                            page = '1'                # IF NOT FOUND, DEFAULT = 1
                            for index in range(1, len(item_recos)):    # SEARCH FROM BOX-2
                                item_reco = item_recos[index]
                                num_list = re.findall(r"\d+\.?\d*", item_reco)
                                if len(num_list) >= 1:
                                    page = num_list[0]
                                    break
                            item_recos[0] = page
                            for index in range(len(item_recos) - 1, 0, -1):    # NOT-RELATED DELETION
                                del item_recos[index]
                                del item_boxes[index]
                    return True, key
                else:
                    return False, key
            else:
                return False, key
        except:
            return True, key

    def without_value_key_deletion(self, item_recos, item_boxes, reco_result, key_or_not):
        try:
            if len(item_recos) > 0 and item_recos[0] != '':
                for index in range(0, len(reco_result)):
                    if reco_result[index] == item_recos[0]:
                        if key_or_not[index]:
                            if not self.key_del_serve_without([item_recos[0].lower()]) == 'KEEP':
                                del item_recos[0]
                                del item_boxes[0]
                        return
        except:
            pass

    def key_del_serve_without(self, item_reco):
        colon_index = item_reco[0].find(":")
        if colon_index > 0 and colon_index + 1 == len(item_reco[0]):
            return
        if self.keyword_check(item_reco[0]):
            return
        return 'KEEP'

    def keyword_check(self, item_reco):
        len_of_item_reco = len(item_reco)
        key_list = ['number', 'numbor', 'consignee', 'price', 'code', 'currency', 'master no', 'sales person',
                                'name', 'address', 'sender', 'country of origin', 'dimensions', 'cnt no', 'coo',
                                'dimension', 'shipper', 'seller', 'eccn', 'qty', 'incoterms', 'destination', 'total no. of ctn',
                                'cartons', 'page', 'forwarding agent/broker', 'miscellanous', 'signature', 'customer po',
                                'salesman', 'ship via', 'payment terms', 'bm/plt', 'total packages', 'total value',
                                'swift', 'service', 'rdd', 'ship mode', 'forwarding agent', 'inland freight', 'freight',
                                'terms of sale', 'end user/title holder', 'mode of transport', 'date of issue', 'carrier',
                                'mawb no', 'hawb no', 'id', '#', 'by', 'from', 'type', 'date', 'terms', 'term', 'no.']

        for item in key_list:
            item_index = item_reco.find(item)
            len_of_item = len(item)
            if item_index >= 0:
                if item_index + len_of_item == len_of_item_reco:
                    return True
                elif item_index + len_of_item + 1 == len_of_item_reco:
                    if item_reco[item_index + len_of_item] == ' ' \
                        or item_reco[item_index + len_of_item] == '.':
                            return True
                    else:
                        return False
                else:
                    return False
        return False

    def with_value_key_deletion(self, key, item_recos):
        try:
            key = key.strip()
            if len(item_recos) > 0 and key == item_recos[0].strip():
                colon_index = item_recos[0].find(":")
                if colon_index > 0:
                    key = key[:colon_index]
                    item_recos[0] = item_recos[0][colon_index + 1:]
                    return key
                if len(item_recos) == 1:
                    key_list = ['number', 'numbor', 'consignee', 'price', 'code', 'currency', 'master no', 'sales person',
                                'name', 'address', 'sender', 'country of origin', 'dimensions', 'cnt no', 'coo',
                                'dimension', 'shipper', 'seller', 'eccn', 'qty', 'incoterms', 'destination', 'total no. of ctn',
                                'cartons', 'page', 'forwarding agent/broker', 'miscellanous', 'signature', 'customer po',
                                'salesman', 'ship via', 'payment terms', 'bm/plt', 'total packages', 'total value',
                                'swift', 'service', 'rdd', 'ship mode', 'forwarding agent', 'inland freight', 'freight',
                                'terms of sale', 'end user/title holder', 'mode of transport', 'date of issue', 'carrier',
                                'mawb no', 'hawb no', 'id', '#', 'by', 'from', 'type', 'date', 'terms', 'term', 'no.']
                    lower_key = key.lower()
                    for index in range(len(key_list)):
                        key_index = lower_key.find(key_list[index])
                        if key_index >= 0:
                            key_length = len(key_list[index])
                            key = key[:key_index + key_length]
                            if len(item_recos[0]) > key_index + key_length:
                                if item_recos[0][key_index + key_length] == ' ' or \
                                   item_recos[0][key_index + key_length] == '.':
                                      item_recos[0] = item_recos[0][key_index + key_length + 1:]
                                else:
                                      item_recos[0] = item_recos[0][key_index + key_length:]
                                return key
                            return key
                    return key
                else:
                    return key
            else:
                return key
        except:
            return key

    def total_optimize(self, key, item_recos):
        if len(item_recos) > 0:
            for index in range(len(item_recos)):
                colon_index = item_recos[index].find(':')
                total_index = item_recos[index].lower().find('total')
                if colon_index >= 0:
                    if len(item_recos[index]) > colon_index + 1:
                        key = key[:colon_index]
                        item_recos[index] = item_recos[index][colon_index + 1:]
                    else:
                        item_recos[index] = ''
                    return key
                else:
                    if total_index >= 0:
                        if len(item_recos[index]) > total_index + 6:
                            if item_recos[index][total_index + 5] == ' ' \
                                and item_recos[index][total_index + 6].isdigit():
                                    key = key[:total_index + 5]
                                    item_recos[index] = item_recos[index][total_index + 6:]
                            else:
                                item_recos[index] = ''
                        else:
                            item_recos[index] = ''
                        return key
                    else:
                        return key
        else:
            return key
        
    def key_equals_to_value(self, key, item_recos, item_boxes):
        if len(item_recos) > 0:
            if key == item_recos[0]:
                if len(item_recos) > 1:
                    del item_recos[0]
                    del item_boxes[0]
                return key
            else:
                return key
        else:
            return key

    def colon_point_space_bracket_deletion(self, key, item_recos):
        try:
            if len(item_recos) > 0:
                for index in range(len(item_recos)):
                    if len(item_recos[index]) > 1:
                        cycle_times = 0
                        while True:
                            change = False
                            if item_recos[index][0] == ':' \
                                or item_recos[index][0] == ','\
                                or item_recos[index][0] == '.' \
                                or item_recos[index][0] == ' ' \
                                or item_recos[index][0] == ')' \
                                or item_recos[index][0] == '-' :
                                    change = True
                                    item_recos[index] = item_recos[index][1:]
                            if item_recos[index][-1] == ':'\
                                or item_recos[index][-1] == ','\
                                or item_recos[index][-1] == '.'\
                                or item_recos[index][-1] == ' '\
                                or item_recos[index][-1] == '('\
                                or (item_recos[index][-1] == ')' and item_recos[index].find('(') < 0):
                                    change = True
                                    item_recos[index] = item_recos[index][:-1]
                            cycle_times += 1
                            if not change or cycle_times == 3:
                                break

            cycle_times = 0
            while True:
                change = False

                if key[0] == '(' and key[-1] == ')':
                    key = key[1:-1]
                    change = True
                if key[0] == ':' or key[0] == ',' or key[0] == '.' or key[0] == ' ' or key[0] == '(' or key[0] == ')':
                    key = key[1:]
                    change = True
                if key[-1] == ':' or key[-1] == ',' or key[-1] == '.' or key[-1] == ' ' or key[-1] == '(' or (key[-1] == ')' and key.find('(') < 0):
                    key = key[:-1]
                    change = True

                if key.find('(') * key.find(')') < 0:
                    if key.find('(') >= 0:
                        key = key[:key.find('(')] + ' ' + key[key.find('(') + 1:]
                    else:
                        key = key[:key.find(')')] + ' ' + key[key.find(')') + 1:]

                cycle_times += 1
                if not change or cycle_times == 3:
                    break

            return key
        except:
            return key

    def single_clean_process(self, item_recos, item_boxes):
        for index in range(len(item_recos) - 1, -1, -1):
            if len(item_recos[index]) == 1:
                if item_recos[index] == ' ' \
                    or item_recos[index] == '.' \
                    or item_recos[index] == ':' \
                    or item_recos[index] == '(' \
                    or item_recos[index] == ')' \
                    or item_recos[index] == ',':
                        del item_recos[index]
                        del item_boxes[index]

    def from_to_er_ee_address_del(self, key, item_recos):
        key_list = ['bill to', 'bili to', 'sold to', 'consignee to', 'ship to', 'forward to', 'invoice to', 'ship from',
                    'shipped from', 'invoice from', 'accountee', 'consignee', 'seller', 'shipper', 'exporter', 'address']
        for item in key_list:
            if key.lower().find(item) >= 0:
                if len(item_recos) < 3 and not len(item_recos) == 1:
                    return True
                else:
                    return False

    def overlap(self, box1_x1, box1_x2, box2_x1, box2_x2):
        length1 = box1_x2 - box1_x1
        length2 = box2_x2 - box2_x1

        overlap_x2 = min(box1_x2, box2_x2)
        overlap_x1 = max(box1_x1, box2_x1)

        overlap_length = overlap_x2 - overlap_x1

        return overlap_length / min(length1, length2)

    def get_average(self, list):
       sum = 0
       for item in list:
          sum += item
       return sum/len(list)

    def IOU(self, bbox_a, bbox_b):
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

        if ratio > 0.7:
            return True
        else:
            return False

    def boxes_to_list(self, boxes_list):
        boxes_list_ = []
        for boxes in boxes_list:
            boxes_ = []
            for box in boxes:
                box_ = box.tolist()
                boxes_.append(box_)
            boxes_list_.append(boxes_)
        return boxes_list_

    def del_aggregation_boxes(self, recos_list, boxes_list, item_boxes):
        for index in range(len(boxes_list)):
            break_sign = False
            agg_boxes = boxes_list[index]
            for agg_box in agg_boxes:
                for item_box in item_boxes:
                    if self.IOU(agg_box, item_box):
                        del recos_list[index]
                        del boxes_list[index]
                        break_sign = True
                        break
                if break_sign:
                    break
            if break_sign:
                break

    def get_recos_boxes(self, key):
        item_recos = []
        item_boxes = []

        recos_temp = self.page.content_list[self.final_result_idxs[key]]
        boxes_temp = self.page.box_list    [self.final_result_idxs[key]]
        boxes_temp = self._change_boxes(boxes_temp)

        index_list, _ = sort_box_by_row(np.array(boxes_temp))
        for index in range(len(index_list)):
            item = index_list[index]
            for sub_index in range(len(item)):
                sub_item = item[sub_index]
                item_recos.append(recos_temp[sub_item])
                item_boxes.append(boxes_temp[sub_item])

        return item_recos, item_boxes
