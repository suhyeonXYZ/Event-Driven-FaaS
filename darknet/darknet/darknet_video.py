from ctypes import *
import random
import os
import cv2
import time
import darknet
import argparse
from threading import Thread, enumerate
from queue import Queue
import pika
import sqlite3
import requests

#rtsp_url = 'rtsp://admin:123456789a@faasoong.iptime.org:554'
amqp_url = 'amqp://faasoong:tnd@116.89.189.12:5672/'
video = './test.mp4'
weight = '/home2/faasoong/Workspace/training/weight back/accident_fire_gun_knife_320x320/yolov4-faasoong_final.weights'
#'./yolov4-faasoong_final.weights'

cfg = '/home2/faasoong/Workspace/training/darknet/build/darknet/x64/cfg/yolov4-faasoong.cfg'
data = './data/obj.data'

def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default=video,
                        help="test.mp4 input")
    parser.add_argument("--out_filename", type=str, default="output.jpg",
                        help="inference video name. Not saved if empty")
    parser.add_argument("--weights", default= weight,
                        help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true',
                        help="windown inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true',
                        help="display bbox coordinates of detected objects")
    parser.add_argument("--config_file", default=cfg,
                        help="path to config file")
    parser.add_argument("--data_file", default= data,
                        help="path to data file")
    parser.add_argument("--thresh", type=float, default=.3,
                        help="remove detections with confidence below this value")
    return parser.parse_args()


def str2int(video_path):
    """
    argparse returns and string althout webcam uses int (0, 1 ...)
    Cast to int if needed
    """
    try:
        return int(video_path)
    except ValueError:
        return video_path


def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    if str2int(args.input) == str and not os.path.exists(args.input):
        raise(ValueError("Invalid video path {}".format(os.path.abspath(args.input))))


def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    video = cv2.VideoWriter(output_video, fourcc, fps, size)
    return video


def convert2relative(bbox):
    """
    YOLO format use relative coordinates for annotation
    """
    x, y, w, h  = bbox
    _height     = darknet_height
    _width      = darknet_width
    return x/_width, y/_height, w/_width, h/_height


def convert2original(image, bbox):
    x, y, w, h = convert2relative(bbox)

    image_h, image_w, __ = image.shape

    orig_x       = int(x * image_w)
    orig_y       = int(y * image_h)
    orig_width   = int(w * image_w)
    orig_height  = int(h * image_h)

    bbox_converted = (orig_x, orig_y, orig_width, orig_height)

    return bbox_converted


def convert4cropping(image, bbox):
    x, y, w, h = convert2relative(bbox)

    image_h, image_w, __ = image.shape

    orig_left    = int((x - w / 2.) * image_w)
    orig_right   = int((x + w / 2.) * image_w)
    orig_top     = int((y - h / 2.) * image_h)
    orig_bottom  = int((y + h / 2.) * image_h)

    if (orig_left < 0): orig_left = 0
    if (orig_right > image_w - 1): orig_right = image_w - 1
    if (orig_top < 0): orig_top = 0
    if (orig_bottom > image_h - 1): orig_bottom = image_h - 1

    bbox_cropping = (orig_left, orig_top, orig_right, orig_bottom)

    return bbox_cropping


def video_capture(frame_queue, darknet_image_queue):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (darknet_width, darknet_height),
                                   interpolation=cv2.INTER_LINEAR)
        frame_queue.put(frame)
        img_for_detect = darknet.make_image(darknet_width, darknet_height, 3)
        darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
        darknet_image_queue.put(img_for_detect)
    cap.release()


def inference(darknet_image_queue, detections_queue, fps_queue):
    accident, fire, people, gun, knife = 0,0,0,0,0
    while cap.isOpened():
        darknet_image = darknet_image_queue.get()
        prev_time = time.time()
        detections = darknet.detect_image(network, class_names, darknet_image, thresh=args.thresh)
        # print(detections)
#        for i in detections:
#            if i[0] == 'accident': accident += 1
#            elif i[0] == 'fire': fire += 1
#            elif i[0] == 'people': people += 1
#            elif i[0] == 'gun': gun += 1
#            elif i[0] == 'knife': knife += 1
#            else: accident, fire, people, gun, knife = 0,0,0,0,0
#        if accident >= 5 :
#            trigger('accident')
#            accident = 0
#        elif fire >= 5 :
#            trigger('fire')
#            fire = 0
#        elif people >= 5 :
#            trigger('people')
#            people = 0
#        elif gun >= 5 :
#            trigger('gun')
#            gun = 0
#        elif knife >= 5 :
#            trigger('knife')
#            knife = 0
        for i in detections:
            if i[0] == 'accident': trigger('accident')
            elif i[0] == 'fire': trigger('accident')
            elif i[0] == 'people': trigger('accident')
            elif i[0] == 'gun': trigger('accident')
            elif i[0] == 'knife':trigger('accident') 
            else: pass 
        

        detections_queue.put(detections)
        fps = int(1/(time.time() - prev_time))
        fps_queue.put(fps)
        print("FPS: {}".format(fps))
        darknet.print_detections(detections, args.ext_output)
        darknet.free_image(darknet_image)
    cap.release()

def trigger(detecting_object):
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.queue_declare(queue=detecting_object)
    channel.basic_publish(exchange='', routing_key=detecting_object, body='100')
    print(" [x] Sent to {}".format(detecting_object))
    connection.close()
    

def drawing(frame_queue, detections_queue, fps_queue):
    random.seed(3)  # deterministic bbox colors
    #video = set_saved_video(cap, args.out_filename, (video_width, video_height))
    while cap.isOpened():
        frame = frame_queue.get()
        detections = detections_queue.get()
        fps = fps_queue.get()
        detections_adjusted = []
        if frame is not None:
            for label, confidence, bbox in detections:
                bbox_adjusted = convert2original(frame, bbox)
                detections_adjusted.append((str(label), confidence, bbox_adjusted))
            image = darknet.draw_boxes(detections_adjusted, frame, class_colors)
            if not args.dont_show:
                #pass
                cv2.imshow('Inference', image)
            if args.out_filename is not None:
                pass
                #video.write(image)
            if cv2.waitKey(fps) == 27:
                break
    cap.release()
    video.release()
    cv2.destroyAllWindows()

def get_rabbitMSG():
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()

    #channel.queue_declare(queue='motion')
    for method_frame, properties, body in channel.consume('motion'):
          # Display the message parts and acknowledge the message
          print(method_frame, properties, body)
          channel.basic_ack(method_frame.delivery_tag)
          # Escape out of the loop after 10 messages
          return body
          if method_frame.delivery_tag == 1:
              break
    return null

if __name__ == '__main__':
    msg_string = get_rabbitMSG().decode('utf-8')
    latitude, longtitude, rtsp_url = msg_string.split('&')
    URL = 'http://amp.paasta.koren.kr/dbinsert.php?latitude='+latitude+'&longtitude='+longtitude
    response = requests.get(URL) 

    print(response.text)
    #response.status_code 
    #response.text




    frame_queue = Queue()
    darknet_image_queue = Queue(maxsize=1)
    detections_queue = Queue(maxsize=1)
    fps_queue = Queue(maxsize=1)

    args = parser()
    check_arguments_errors(args)
    network, class_names, class_colors = darknet.load_network(
            args.config_file,
            args.data_file,
            args.weights,
            batch_size=1
    )
    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    #input_path = str2int(args.input)
    cap = cv2.VideoCapture(rtsp_url)#input_path)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    Thread(target=video_capture, args=(frame_queue, darknet_image_queue)).start()
    Thread(target=inference, args=(darknet_image_queue, detections_queue, fps_queue)).start()
    Thread(target=drawing, args=(frame_queue, detections_queue, fps_queue)).start()

