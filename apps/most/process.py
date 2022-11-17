from .models import *
import datetime
import pytz
import time








"""
____________________JSON______________________________________________________________________________________________________________
"""
# import pymongo
# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
def query_records(cbox, arrival_date_s, arrival_date_e):
    # timeString = "2020-09-09" # 時間格式為字串
    # struct_time = time.strptime(timeString, "%Y-%m-%d") # 轉成時間元組
    # time_stamp = int(time.mktime(struct_time)) # 轉成時間戳
    time_list = []
    t=0
    state = 1

    # start
    time1 = time.time()
    state = 1
    try:
        if cbox and arrival_date_s and arrival_date_e:
            # print("都有")
            arrival_date_s = int(time.mktime(time.strptime(arrival_date_s, "%Y-%m-%d")))
            arrival_date_e = int(time.mktime(time.strptime(arrival_date_e, "%Y-%m-%d")))
            records = DetectionRecords.objects.filter(user_id__in = cbox, arrival_time__range=(arrival_date_s, arrival_date_e+86399))
        elif cbox and not arrival_date_s and not arrival_date_e:
            # print("有站點 無時間")
            records = DetectionRecords.objects.filter(user_id__in = cbox)
        elif not cbox and arrival_date_s and arrival_date_e:
            # print("有時間 無站點")
            arrival_date_s = int(time.mktime(time.strptime(arrival_date_s, "%Y-%m-%d")))
            arrival_date_e = int(time.mktime(time.strptime(arrival_date_e, "%Y-%m-%d")))
            records = DetectionRecords.objects.filter(arrival_time__range=(arrival_date_s, arrival_date_e+86399))
        else:
            # print("無效")
            state = 0
    except:
        return None
    
    num = 0
    query_json=[] #每張圖的資訊

    if state == 1:
        # print(records)
        for record in records:
            records_list = {}
            num += 1
            records_list['num'] = num
            records_list['rid'] = record.rid
            records_list['original_img'] = record.original_img  #原圖路徑
            if record.result_img != None:
                records_list['result_img'] = record.result_img  #辨識結果圖路徑
            else:
                records_list['result_img'] = "無辨識結果"
            #上傳時間
            records_list['arrival_time'] = datetime.datetime.utcfromtimestamp(record.arrival_time).replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
            records_list['site_name'] = record.user_id.name  #站點
            records_list['state'] = record.state  # 0:表示無瑕疵 1:表示有瑕疵
            #辨識完成時間
            if record.leave_time != None:
                records_list['spend_time'] = str(record.leave_time - record.arrival_time)+'秒' #辨識耗時
            else:
                records_list['spend_time'] = "無辨識結果"
            #圖片面積(寬*高)
            if record.img_width != None and record.img_height != None:
                img_area = record.img_width * record.img_height
            else:
                img_area = 0
            query_json.append(records_list)
    time2 = time.time()
    loss = time2 - time1
    # print()
    t += loss
    time_list.append(t)
    # end



    # time_list = []
    # t=0
    # state = 1
    # for a in range(100):
    #     time1 = time.time()
    #     state = 1
    #     try:
    #         if cbox and arrival_date_s and arrival_date_e:
    #             # print("都有")
    #             arrival_date_s = int(time.mktime(time.strptime(arrival_date_s, "%Y-%m-%d")))
    #             arrival_date_e = int(time.mktime(time.strptime(arrival_date_e, "%Y-%m-%d")))
    #             records = DetectionRecords.objects.filter(user_id__in = cbox, arrival_time__range=(arrival_date_s, arrival_date_e+86399))
    #         elif cbox and not arrival_date_s and not arrival_date_e:
    #             # print("有站點 無時間")
    #             records = DetectionRecords.objects.filter(user_id__in = cbox)
    #         elif not cbox and arrival_date_s and arrival_date_e:
    #             # print("有時間 無站點")
    #             arrival_date_s = int(time.mktime(time.strptime(arrival_date_s, "%Y-%m-%d")))
    #             arrival_date_e = int(time.mktime(time.strptime(arrival_date_e, "%Y-%m-%d")))
    #             records = DetectionRecords.objects.filter(arrival_time__range=(arrival_date_s, arrival_date_e+86399))
    #         else:
    #             # print("無效")
    #             state = 0
    #     except:
    #         return None
        
    #     num = 0
    #     query_json=[] #每張圖的資訊

    #     if state == 1:
    #         # print(records)
    #         for record in records:
    #             records_list = {}
    #             num += 1
    #             records_list['num'] = num
    #             records_list['rid'] = record.rid
    #             records_list['original_img'] = record.original_img  #原圖路徑
    #             if record.result_img != None:
    #                 records_list['result_img'] = record.result_img  #辨識結果圖路徑
    #             else:
    #                 records_list['result_img'] = "無辨識結果"
    #             #上傳時間
    #             records_list['arrival_time'] = datetime.datetime.utcfromtimestamp(record.arrival_time).replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
    #             records_list['site_name'] = record.user_id.name  #站點
    #             records_list['state'] = record.state  # 0:表示無瑕疵 1:表示有瑕疵
    #             #辨識完成時間
    #             if record.leave_time != None:
    #                 records_list['spend_time'] = str(record.leave_time - record.arrival_time)+'秒' #辨識耗時
    #             else:
    #                 records_list['spend_time'] = "無辨識結果"
    #             #圖片面積(寬*高)
    #             if record.img_width != None and record.img_height != None:
    #                 img_area = record.img_width * record.img_height
    #             else:
    #                 img_area = 0
    #             query_json.append(records_list)
    #     time2 = time.time()
    #     loss = time2 - time1
    #     # print()
    #     t += loss
    #     time_list.append(t)
    # print(time_list)
    #     # print(query_json)
    
    


    # # MongoDB
    # mydb = myclient["ZHIWHALE"]
    # mycol = mydb["Detection"]
    # query_json=[]
    # for j in range(100):
    #     time1 = time.time()
    #     for i in mycol.find():
    #         query_json.append(i)
    #     # # print(query_json)
    #     # print(len(query_json))
    #     time2 = time.time()
    #     loss = time2 - time1
    #     # print()
    #     t += loss
    #     time_list.append(t)
    # print(time_list)
    # # print(t/100)
    return {"query_json":query_json, "state":state}
    


def get_site():
    try:
        get_site = UserInfo.objects.all()
    except:
        return None
        
    site_json = []
    for site in get_site:
        site_list = {}
        site_list['uid'] = str(site.uid)
        site_list['name'] = site.name
        site_json.append(site_list)
    
    return {'site_json': site_json }


def get_detection_records():
    try:
        records = DetectionRecords.objects.all().order_by('-arrival_time')[:5]
        defects = DefectList.objects.all()
    except:
        return None

    records_json = [] #每張圖的資訊
    for record in records:
        records_list = {}
        # records_list['car_number'] = record.car_number
        records_list['original_img'] = record.original_img  #原圖路徑
        if record.result_img != None:
            records_list['result_img'] = record.result_img  #辨識結果圖路徑
        else:
            records_list['result_img'] = "無辨識結果"
        #上傳時間
        records_list['arrival_time'] = datetime.datetime.utcfromtimestamp(record.arrival_time).replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
        records_list['site_name'] = record.user_id.name  #站點
        records_list['state'] = record.state  # 0:表示無瑕疵 1:表示有瑕疵
        #辨識完成時間
        if record.leave_time != None:
            records_list['spend_time'] = str(record.leave_time - record.arrival_time)+'秒' #辨識耗時
        else:
            records_list['spend_time'] = "無辨識結果"
        #圖片面積(寬*高)
        if record.img_width != None and record.img_height != None:
            img_area = record.img_width * record.img_height
        else:
            img_area = 0
            

        # 車有瑕疵
        if record.state == 1:
            defects_json = [] #瑕疵車的資訊
            num = 0
            defect_area = 0
            for defect in defects:
                if defect.car_id.rid == record.rid:
                    defects_list = {} #瑕疵明細
                    num += 1
                    defects_list['num'] = num #第N個瑕疵
                    #瑕疵類別
                    if defect.class_ids == 1:
                        defects_list['class_ids'] = "刮痕 (scratch)"
                    elif defect.class_ids == 2:
                        defects_list['class_ids'] = "凹痕 (dent)"
                    #概率分數(probability scores)
                    defects_list['scores'] = defect.scores
                    defects_list['scores_1f'] = str('%.1f'%float(defect.scores*100))+'%'  #概率分數(換算百分比)
                    #單個瑕疵範圍(defect.defect_range)
                    if defect.defect_range != None:
                        defect_area += defect.defect_range #同一台車的瑕疵範圍加總
                        defects_list['defect_range'] = str(defect.defect_range) + ' pixel'  #單個瑕疵範圍(單位：pixel)
                        #單個bbox範圍
                        defects_list['bbox_range'] = str(abs(defect.rois_y1 - defect.rois_y2) * abs(defect.rois_x1 - defect.rois_x2)) + ' pixel'
                        #單個瑕疵佔bbox的面積
                        defects_list['defect_area_percent'] = str('%.1f'%float(defect.defect_range / (abs(defect.rois_y1 - defect.rois_y2) * abs(defect.rois_x1 - defect.rois_x2))*100)) + '%'
                    else:
                        defects_list['defect_range'] = "尚無資料"
                        defects_list['bbox_range'] = "尚無資料"
                    defects_json.append(defects_list)
            #全部瑕疵佔整張圖的面積
            if img_area != 0 :
                records_list['defect_area_percent'] = str('%.1f'%float(defect_area / img_area * 100)) + '%'
            else:
                records_list['defect_area_percent'] = "尚無資料"
            #同一台車的瑕疵總數量
            records_list['num'] = num
            records_list['defect_array'] = defects_json #同一台瑕疵車的所有資訊
        # 車無瑕疵
        elif record.state == 0:
            records_list['defect_array'] = "辨識結果：無瑕疵"
        records_json.append(records_list)
   
    return {'detection_records': records_json }


def user_profile(uid,code):
    try:
        user = UserInfo.objects.get(uid = uid)
    except:
        return None
    user_profile = {}
    user_profile['uid'] = user.uid
    user_profile['name'] = user.name

    
    #判斷左側選單狀態
    item_state = {}
    index_item_state = 0
    query_item_state = 0
    if code == 'index':
        index_item_state = 1
    elif code == 'query':
        query_item_state = 1
    item_state['index_item_state'] = index_item_state
    item_state['query_item_state'] = query_item_state
    # print(item_state)
    
    return {'user_profile': user_profile, 'item_state':item_state }
