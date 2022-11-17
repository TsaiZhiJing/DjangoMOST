# -*- coding: utf-8 -*-
import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import cv2
import time
from mrcnn.config import Config
from datetime import datetime
# Root directory of the project
ROOT_DIR = os.getcwd()
 
# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library
# from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize


class ShapesConfig(Config):
    """Configuration for training on the toy shapes dataset.
    Derives from the base Config class and overrides values specific
    to the toy shapes dataset.
    """
    # Give the configuration a recognizable name
    NAME = "shapes"
 
    BACKBONE = "resnet50"  # resnet34 or resnet50 or resnet101

    # Train on 1 GPU and 8 images per GPU. We can put multiple images on each
    # GPU because the images are small. Batch size is 8 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
 
    # Number of classes (including background)
    NUM_CLASSES = 1 + 2  # background + 3 shapes
 
    # Use small images for faster training. Set the limits of the small side
    # the large side, and that determines the image shape.
    IMAGE_MIN_DIM = 320
    IMAGE_MAX_DIM = 384
 
    # Use smaller anchors because our image and objects are small
    RPN_ANCHOR_SCALES = (8 * 6, 16 * 6, 32 * 6, 64 * 6, 128 * 6)  # anchor side in pixels
 
    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    TRAIN_ROIS_PER_IMAGE = 100
 
    # Use a small epoch since the data is simple
    STEPS_PER_EPOCH = 100
 
    # use small validation steps since the epoch is small
    VALIDATION_STEPS = 50
 
#import train_tongue
#class InferenceConfig(coco.CocoConfig):
class InferenceConfig(ShapesConfig):
    # Set batch size to 1 since we'll be running inference on
    # one image at a time. Batch size = GPU_COUNT * IMAGES_PER_GPU
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

def MaskRCNN(img_name):

    # Import COCO config
    # sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
    # from samples.coco import coco
    time1 = time.time()
    
    
    # Directory to save logs and trained model
    MODEL_DIR = os.path.join("logs")
    
    # Local path to trained weights file
    COCO_MODEL_PATH = os.path.join(MODEL_DIR ,"mask_rcnn_shapes_0030.h5")

    
    # Directory of images to run detection on
    IMAGE_DIR = os.path.join(ROOT_DIR, "media", img_name)

    print(IMAGE_DIR)





    inference_config = InferenceConfig()
    
    # Create model object in inference mode.
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=inference_config)
    
    # Load weights trained on MS-COCO
    model.load_weights(COCO_MODEL_PATH, by_name=True)
    
    # COCO Class names
    # Index of the class in the list is its ID. For example, to get ID of
    # the teddy bear class, use: class_names.index('teddy bear')
    # class_names = ['BG', 'scratch', 'dent']
    class_names = ['BG', 'scratch', 'dent']
    
    # Load a random image from the images folder
    # file_names = next(os.walk(IMAGE_DIR))[2]
    image = skimage.io.imread(IMAGE_DIR)  #輸入圖片的路徑
    
    # a=datetime.now()
    # Run detection
    results = model.detect([image], verbose=1)
    # b=datetime.now()
    # Visualize results
    # print("shijian",(b-a).seconds)



    
    # print(results)
    # print('--------------------------------------------------')
    # print(results[0])
    # print('--------------------------------------------------')
    # print("rois", results[0]['rois'])           #rois [[249 575 438 777], [535 449 685 715]]
    # print('--------------------------------------------------')
    # print("masks", results[0]['masks'])
    # print('--------------------------------------------------')
    # print("class_ids", results[0]['class_ids']) #class_ids [2, 1]   (1:scratch,  2:dent)
    # print('--------------------------------------------------')
    # print("scores", results[0]['scores'])       #scores [0.9952494,  0.92597884]
    # print('--------------------------------------------------')
    # print(len(results[0]['rois']))

    # defect_json = []
    # for i in range(len(results[0]['rois'])):
    #     defect_list = {}
    #     defect_list['rois'] = results[0]['rois'][i]
    #     defect_list['masks'] = results[0]['masks'][i]
    #     defect_list['class_ids'] = results[0]['class_ids'][i]
    #     defect_list['scores'] = results[0]['scores'][i]
    #     defect_json.append(defect_list)




        

    r = results[0]
    # visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'],
    #                             class_names, r['scores'])


    masked_image, defect_range_json =visualize.cv_process(image, r['rois'], r['masks'], r['class_ids'],class_names, r['scores'])
    # print('masked_image', masked_image)
    # print('defect_range_json', defect_range_json)

    # result_img_path = "/media/output/"+img_name 
    save_img_path = os.path.join(ROOT_DIR, "media", "output", img_name) #儲存圖片的路徑
    cv2.imwrite(save_img_path, masked_image[:,:,(2,1,0)])
    result_img_path = "media/output/"+img_name #輸出圖片的路徑

    time2 = time.time()
    print(time2 - time1)
    return result_img_path, results[0], defect_range_json