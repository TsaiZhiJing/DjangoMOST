from django.db import models

class UserInfo(models.Model):
    uid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    class Meta:
        db_table = 'user_info'

class DetectionRecords(models.Model):
    rid = models.AutoField(primary_key=True)
    # car_number = models.CharField(max_length=20) #車牌
    user_id= models.ForeignKey('UserInfo', related_name='user_detection_records',on_delete=models.CASCADE) #站點
    arrival_time = models.IntegerField(null = True, blank = True) #到站時間
    leave_time = models.IntegerField(null = True, blank = True) #離站時間
    original_img = models.CharField(max_length=200, null=True) #原始照片
    result_img = models.CharField(max_length=200, null=True) #辨識結果圖
    state = models.PositiveSmallIntegerField(null=False) #狀態
    img_width = models.IntegerField(null = True, blank = True) #圖片寬
    img_height = models.IntegerField(null = True, blank = True) #圖片高
    class Meta:
        db_table = 'detection_records'

class DefectList(models.Model):
    did = models.AutoField(primary_key=True)
    car_id= models.ForeignKey('DetectionRecords', related_name='car_defect_list',on_delete=models.CASCADE) #車輛
    rois_y1 = models.IntegerField(null = True, blank = True) #detection bounding boxes y1
    rois_x1 = models.IntegerField(null = True, blank = True) #detection bounding boxes x1
    rois_y2 = models.IntegerField(null = True, blank = True) #detection bounding boxes y2
    rois_x2 = models.IntegerField(null = True, blank = True) #detection bounding boxes x2
    class_ids = models.PositiveSmallIntegerField(null=False) #類別 ((1:scratch(刮痕),  2:dent(凹痕))
    scores = models.DecimalField(max_digits=10, decimal_places=8) #概率分數
    defect_range = models.IntegerField(null = True, blank = True) #defect range
    class Meta:
        db_table = 'defect_list'
