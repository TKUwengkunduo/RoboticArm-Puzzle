"""
    YOLO & Python 環境需求
        1. .data
        2. .name
        3. .cfg
        4. .weight
        5. darknet(shared library)
        6. darknet.py
        7. libdarknet.so
"""


import time
import cv2
import numpy as np
import darknet



# video = cv2.VideoCapture("/home/weng/ICLAB/output2.avi")

# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out_video = cv2.VideoWriter('demo_YOLO_2.avi', fourcc, 15.0, (1280,  720))


"""
神經網路檔案位置_檢測全部拼圖
"""
Full_Puzzle_cfg_path = '/home/weng/RoboticArm_Puzzle/main/cfg/Full_Puzzle.cfg'
Full_Puzzle_weights_path = '/home/weng/RoboticArm_Puzzle/main/cfg/weights/Full_Puzzle/yolov4-tiny-obj_70000.weights'
Full_Puzzle_data_path = '/home/weng/RoboticArm_Puzzle/main/cfg/Full_Puzzle.data'

"""
神經網路檔案位置_檢測凸點
"""
Feature_Point_cfg_path = '/home/weng/RoboticArm_Puzzle/main/cfg/Feature_Point.cfg'
Feature_Point_weights_path = '/home/weng/RoboticArm_Puzzle/main/cfg/weights/Feature_Point/yolov4-tiny-obj_best.weights'
Feature_Point_data_path = '/home/weng/RoboticArm_Puzzle/main/cfg/Feature_Point.data'



"""
載入神經網路
"""
Full_Puzzle_network, Full_Puzzle_class_names, Full_Puzzle_class_colors = darknet.load_network(
        Full_Puzzle_cfg_path,
        Full_Puzzle_data_path,
        Full_Puzzle_weights_path,
        batch_size=1
)

"""
載入神經網路
"""
Feature_Point_network, Feature_Point_class_names, Feature_Point_class_colors = darknet.load_network(
        Feature_Point_cfg_path,
        Feature_Point_data_path,
        Feature_Point_weights_path,
        batch_size=1
)




"""
影像檢測
    輸入:(影像位置,神經網路,物件名稱集,信心值閥值(0.0~1.0))
    輸出:(檢測後影像,檢測結果)
    註記:
"""
def image_detection(image, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)

    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    image = darknet.draw_boxes(detections, image_resized, class_colors)

    print(detections)

    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections



"""
座標轉換
    輸入:(YOLO座標,原圖寬度,原圖高度)
    輸出:(框的左上座標,框的右下座標)
    註記:
"""
def bbox2points(bbox,W,H):
    """
    From bounding box yolo format
    to corner points cv2 rectangle
    """ 
    width = darknet.network_width(Full_Puzzle_network)      # YOLO壓縮圖片大小(寬)
    height = darknet.network_height(Full_Puzzle_network)    # YOLO壓縮圖片大小(高)

    x, y, w, h = bbox                           # (座標中心x,座標中心y,寬度比值,高度比值)
    x = x*W/width
    y = y*H/height
    w = w*W/width
    h = h*H/height
    # 輸出框座標_YOLO格式
    # print("     (left_x: {:.0f}   top_y:  {:.0f}   width:   {:.0f}   height:  {:.0f})".format(x, y, w, h))
    x1 = int(round(x - (w / 2)))
    x2 = int(round(x + (w / 2)))
    y1 = int(round(y - (h / 2)))
    y2 = int(round(y + (h / 2)))
    
    return x1, y1, x2, y2



"""
原圖繪製檢測框線
    輸入:(檢測結果,原圖位置,框線顏色集)
    輸出:(影像結果)
    註記:
"""
def draw_boxes(detections, image, colors):
    yolo_info = [[-999 for i in range(2)] for j in range(35)]

    H,W,_ = image.shape                         # 獲得原圖長寬
    img = image.copy()

    for label, confidence, bbox in detections:
        x1, y1, x2, y2 = bbox2points(bbox,W,H)

        cv2.rectangle(img, (x1, y1), (x2, y2), colors[label], 1)
        cv2.putText(img, "{} [{:.2f}]".format(label, float(confidence)),
                    (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    colors[label], 2)
        # 輸出框座標_加工格式座標(左上點座標,右上點座標)
        print("\t{}\t: {:3.2f}%    (x1: {:4.0f}   y1: {:4.0f}   x2: {:4.0f}   y2: {:4.0f})".format(label, float(confidence), x1, y1, x2, y2))

        yolo_info[int(label)-1] = [ ((x1+x2)/2) , ((y1+y2)/2) ]
        # print(yolo_info)
        # yolo_info[num][1] = [ ((x1+x2)/2) , ((y1+y2)/2) ]

    return img, yolo_info


def detect_ALL(img,thresh=0.8):
    out,detections = image_detection(img,Full_Puzzle_network, Full_Puzzle_class_names, Full_Puzzle_class_colors,thresh)
    out2,yolo_info = draw_boxes(detections, img, Full_Puzzle_class_colors)
    # txt=open('predict.txt','w+')
    # for o in range(len(detections)):
    #     txt.write('{} {} {} {} {}\n'.format(detections[o][0],detections[o][2][0],detections[o][2][1],detections[o][2][2],detections[o][2][3]))
    # txt.close()
    cv2.imshow('out2', out2)
    # cv2.waitKey(1000)
    # cv2.destroyAllWindows()

    return yolo_info


def detect_Angle(img,thresh=0.3):
    out,detections = image_detection(img,Feature_Point_network, Feature_Point_class_names, Feature_Point_class_colors,thresh)
    out2,yolo_info = draw_boxes(detections, img, Feature_Point_class_colors)
    # txt=open('predict_f.txt','w+')
    # for o in range(len(detections)):
    #     txt.write('{} {} {} {} {}\n'.format(detections[o][0],detections[o][2][0],detections[o][2][1],detections[o][2][2],detections[o][2][3]))
    # txt.close()
    cv2.imshow('out2', out2)
    # cv2.waitKey(1000)
    # cv2.destroyAllWindows()

    return yolo_info



"""
主程式
    程式流程:
    1. 檢測影像
    2. 在原圖繪製結果
    3. 輸出影像
"""
if __name__ == "__main__":

    img_name = '/home/weng/Downloads/16339125841567.jpg'
    image = cv2.imread(img_name)

    # yolo_info = detect_ALL(image)    
    # print(yolo_info)
    # cv2.waitKey(3000)

    print("=============================================")
    image = cv2.imread(img_name)
    yolo_info = detect_Angle(image) 
    for i in range(len(yolo_info)):
        print(i,"=",yolo_info[i])
    cv2.waitKey(0)

    image = cv2.imread(img_name)
    yolo_info = detect_ALL(image) 
    for i in range(len(yolo_info)):
        print(i,"=",yolo_info[i])
    cv2.waitKey(0)

    # out,detections = image_detection(image,Full_Puzzle_network, Full_Puzzle_class_names, Full_Puzzle_class_colors,0.8)

    # out2, yolo_info = draw_boxes(detections, image, Full_Puzzle_class_colors)
    # # out_video.write(out2)

    # #cv2.imshow('out', out)      # YOLO壓縮大小
    # cv2.imshow('out2', out2)    # 原圖
    # cv2.waitKey(3000)




    # while 1:
    #     # ret, image = video.read()
    #     detections = 0  #detections歸零(以後迴圈可能會有影響)
    #     out,detections = image_detection(image,Full_Puzzle_network, Full_Puzzle_class_names, Full_Puzzle_class_colors,0.8)

    #     out2, yolo_info = draw_boxes(detections, image, Full_Puzzle_class_colors)
    #     # out_video.write(out2)

    #     #cv2.imshow('out', out)      # YOLO壓縮大小
    #     cv2.imshow('out2', out2)    # 原圖
    #     # cv2.waitKey(0)


    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

# video.release()
# out_video.release()
cv2.destroyAllWindows()







# 參考資料
# https://blog.csdn.net/Cwenge/article/details/80389988
# https://www.google.com/search?q=libdarknet.so+%E6%89%BE%E4%B8%8D%E5%88%B0&oq=libdarknet.so+%E6%89%BE%E4%B8%8D%E5%88%B0&aqs=chrome..69i57j33i160l2.9119j0j4&sourceid=chrome&ie=UTF-8