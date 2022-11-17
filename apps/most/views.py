from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .process import *
from django.core.files.storage import FileSystemStorage
import time
import cv2, os



#瑕疵明細
def detail(request, pk):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    uid = request.session.get('uid', None)
    site = request.session.get('site', None)
    code = 'query'
            
    record = get_object_or_404(DetectionRecords, pk=pk)

    #瑕疵車的資訊
    defects = DefectList.objects.filter(car_id = record)
    defects_json = [] 
    num = 0
    defect_area = 0
    for defect in defects:
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

        

    #車輛資訊
    records_list = {}
    # records_list['car_number'] = record.car_number
    records_list['original_img'] = record.original_img  #原圖路徑
    if record.result_img != None:
        records_list['result_img'] = record.result_img  #檢測結果圖路徑
    else:
        records_list['result_img'] = "無檢測結果"
    #上傳時間
    records_list['arrival_time'] = datetime.datetime.utcfromtimestamp(record.arrival_time).replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M:%S")
    records_list['site_name'] = record.user_id.name  #站點
    records_list['state'] = record.state  # 0:表示無瑕疵 1:表示有瑕疵
    #檢測完成時間
    if record.leave_time != None:
        records_list['spend_time'] = str(record.leave_time - record.arrival_time)+'秒' #檢測耗時
    else:
        records_list['spend_time'] = "無檢測結果"
    #圖片面積(寬*高)
    if record.img_width != None and record.img_height != None:
        img_area = record.img_width * record.img_height
    else:
        img_area = 0
    #全部瑕疵佔整張圖的面積
    if img_area != 0 :
        records_list['defect_area_percent'] = str('%.1f'%float(defect_area / img_area * 100)) + '%'
    else:
        records_list['defect_area_percent'] = "尚無資料"
    #同一台車的瑕疵總數量
    records_list['num'] = num



    return render(request, 'detail.html', {**user_profile(uid,code), 'defects_json':defects_json, 'record':records_list})




#查詢
def query(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    uid = request.session.get('uid', None)
    site = request.session.get('site', None)
    code = 'query'

    cbox = ""
    arrival_date_s = ""
    arrival_date_e = ""
    profile = {}
    if request.method == "POST":
        
        cbox = request.POST.getlist('cbox', None)
        arrival_date_s = request.POST.get('arrival_date_s', None)
        arrival_date_e = request.POST.get('arrival_date_e', None)

        # 前端顯示
        profile['cbox'] = cbox
        profile['arrival_date_s'] = arrival_date_s
        profile['arrival_date_e'] = arrival_date_e
        


    

    return render(request, 'query.html',{**get_site(), **user_profile(uid,code), **query_records(cbox, arrival_date_s, arrival_date_e), 'profile':profile})




#首頁
def index(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    uid = request.session.get('uid', None)
    site = request.session.get('site', None)
    code = 'index'
    
    # CAR_NUMBER = {'014':'DL4CAS2212', '034':'DL5CJ6551', '038':'DL9CA04652',
    #                 '043':'DL5CN6523', '078':'DL4CAS3293', '080':'DL8CAJ3300', 
    #                 '081':'HR77A0371', '088':'HR13F7709', '091':'DL2CAS9455', 
    #                 '103':'05D37204', '105':'JTS18Y', '144':'HR99ABHT4112', 
    #                 '145':'DL5CN6678', '146':'DL4CAS7521', '235':'DL4CAS8532', 
    #                 '245':'DL8CU2775', '250':'DL9CAA8203', '259':'7667611', '269':'HR791847', '295':'EKM0525'}
    uploaded_file=None
    if request.method == "POST" and 'fileField' in request.FILES:
        fileField = request.FILES['fileField']
        fs = FileSystemStorage()
        img_name = fs.save(fileField.name, fileField)
        uploaded_file=str(fs.url(img_name))
        # for i in CAR_NUMBER:
        #     if fileField.name[:3] == i:
        #         car_number = CAR_NUMBER[i]
        user_id = UserInfo.objects.get(uid=uid)

        #取原圖面積(寬*長)
        ROOT_DIR = os.getcwd()
        IMAGE_DIR = os.path.join(ROOT_DIR, "media", img_name)
        img = cv2.imread(IMAGE_DIR)

        #新增
        record = DetectionRecords.objects.create(user_id = user_id, 
                                                    arrival_time = time.time(), 
                                                    original_img = uploaded_file, 
                                                    state = 0,
                                                    img_height = img.shape[0],
                                                    img_width = img.shape[1])

        #瑕疵檢測
        from .maskrcnn import MaskRCNN
        import tensorflow.compat.v1 as tf
        from tensorflow.keras import backend as K
        K.clear_session()
        tf.reset_default_graph()
        result_img_path, results, defect_range_json = MaskRCNN(img_name)

        #上傳檢測結果
        car_id = DetectionRecords.objects.get(rid = record.rid)
        #若有瑕疵
        if len(results['rois'])!= 0:
            DetectionRecords.objects.filter(rid = record.rid).update(result_img = result_img_path, leave_time = time.time(), state = 1)
            #上傳瑕疵
            for i in range(len(results['rois'])):
                DefectList.objects.create(car_id = car_id, 
                                            rois_y1 = results['rois'][i][0], 
                                            rois_x1 = results['rois'][i][1], 
                                            rois_y2 = results['rois'][i][2],
                                            rois_x2 = results['rois'][i][3], 
                                            class_ids = results['class_ids'][i], 
                                            scores = '%.8f'%float(results['scores'][i]),
                                            defect_range = defect_range_json[i])
        #若無瑕疵
        else:
            DetectionRecords.objects.filter(rid = record.rid).update(result_img = result_img_path, leave_time = time.time(), state = 0)

    elif request.method == "POST" and not('fileField' in request.FILES):
        return render(request, 'index.html', {'site':site, **user_profile(uid,code), **get_detection_records(), 'msg':'錯誤！請選擇照片！'})

    return render(request, 'index.html', {'site':site, **user_profile(uid,code), **get_detection_records()})




#登入
def login(request):
    if request.session.get('is_login', None):
        return redirect('/')
    if request.method == "POST":
        if request.POST.get('submitType', None) == "siteLogin":
            name = request.POST.get('name', None)
            try:
                u = UserInfo.objects.get(name=name)
            except:
                return render(request, 'login.html', {'message':'帳號不存在！'})
            if name == u.name:
                request.session['is_login'] = True
                request.session['uid'] = u.uid
                request.session['site'] = u.name
                return redirect('/')
            else:
                return render(request, 'login.html', {'message':'帳號或密碼錯誤！'})
    return render(request, 'login.html', {**get_site()})

#登出
def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/')
    request.session.flush()
    return redirect('/')