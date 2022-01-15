from django.db.models.manager import Manager
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from blog.models import *
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django import forms
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count
from django.core import serializers
import json
from urllib import parse
from django.contrib import messages
#웹캠 library
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
#twilio sms
from twilio.rest import Client

import boto3
import os
#SMS key(이건 절대노출되면 안됨)
account_sid = 'ACc9d44e3405a3b0e7588a8bb3ccad2456'
auth_token = '05eead392a54f50611b7580c0e48bab8' 
client = Client(account_sid, auth_token)

#google vision & rekognition api
import io
import cv2
import numpy as np
from google.cloud import vision
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon



#초기화면
def about(req):
    return render(req,"blog/about.html")
def contact(req):
    return render(req,"blog/contact.html")
    
def duckyang(req):
    nlist = upload()
    for name in nlist:
        photo = name
        bucket='forstatic'
        client=boto3.client('rekognition',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                            region_name='ap-northeast-2')
        response = client.detect_labels(Image={'S3Object':
        {'Bucket':bucket,'Name':photo}},
                MaxLabels=10)
        flag=0
        for label in response['Labels']:           
            if(label['Name']=='Motorcycle' and label['Confidence']>80):
                print('오토바이 감지')
                flag=1
        
        helmet_flag=0
        flag2=0
        # 오토바이 감지가 된 경우에 헬맷을 썼냐 안썼냐 판별
        if(flag==1):
            for label in response['Labels']:
                if(label['Name']=='Helmet' and label['Confidence']>80):
                    print('헬맷 착용')
                    flag2=1
                else:
                    helmet_flag=1

            #오토바이O  헬맷 X
            if(flag2==0 and helmet_flag == 1):
                configs = config_env("forstatic",photo[11:],"forstatic")
                crop_res = Crop_Image(configs)
                if not len(crop_res):
                    print('No Plate Detected... Terminating Process...')
                    if(photo[11:]=="static.PNG"):
                        continue
                    else:
                        delete_s3Image(photo)
                    
                else:
                    img_format = os.path.splitext(photo[11:])[1]
                    text = [text[0] for text in getTextsCoords(CVToVision(crop_res,img_format), configs[0])][1:]
                   
                    uploadS3(crop_res, configs[len(configs)-1])
                    a = ""
                    for i in text:
                        print(i)
                        a+=i+" "
                    

                    Carnumber = CarNumber()
                    Carnumber.carnumber=a
                    Carnumber.location = photo[11:]
                    Carnumber.locationnumber=parse.quote(photo[11:])
                    Carnumber.date = timezone.now()
                    Carnumber.save()

                    Tmpcarnumber=tmpcarnumber()
                    Tmpcarnumber.carnumber=a
                    Tmpcarnumber.location = photo[11:]
                    Tmpcarnumber.locationnumber=parse.quote(photo[11:])
                    Tmpcarnumber.date = timezone.now()
                    Tmpcarnumber.save()     


        if(photo[11:]!="static.PNG"):
            delete_s3Image(photo)  #s3에있는 이미지파일 삭제
        
    Carnumber_all = CarNumber.objects.filter(location__contains='경기도 고양시 덕양구') 
    json = getjson_duckyang()  
    context={
        'dataset':json,
        "Carnumber_all":Carnumber_all
    }
    return render(req,"blog/duckyang.html",context)

def seocho(req):
    nlist = upload()
    for name in nlist:
        photo = name
        bucket='forstatic'
        client=boto3.client('rekognition',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                            region_name='ap-northeast-2')
        response = client.detect_labels(Image={'S3Object':
        {'Bucket':bucket,'Name':photo}},
                MaxLabels=10)
        flag=0
        for label in response['Labels']:           
            if(label['Name']=='Motorcycle' and label['Confidence']>80):
                print('오토바이 감지')
                flag=1
        
        helmet_flag=0
        flag2=0
        # 오토바이 감지가 된 경우에 헬맷을 썼냐 안썼냐 판별
        if(flag==1):
            for label in response['Labels']:
                if(label['Name']=='Helmet' and label['Confidence']>80):
                    print('헬맷 착용')
                    flag2=1
                else:
                    helmet_flag=1

            #오토바이O  헬맷 X
            if(flag2==0 and helmet_flag == 1):
                configs = config_env("forstatic",photo[11:],"forstatic")
                crop_res = Crop_Image(configs)
                if not len(crop_res):
                    print('No Plate Detected... Terminating Process...')
                    if(photo[11:]=="static.PNG"):
                        continue
                    else:
                        delete_s3Image(photo)
                    
                else:
                    img_format = os.path.splitext(photo[11:])[1]
                    text = [text[0] for text in getTextsCoords(CVToVision(crop_res,img_format), configs[0])][1:]
                   
                    uploadS3(crop_res, configs[len(configs)-1])
                    a = ""
                    for i in text:
                        print(i)
                        a+=i+" "
                    
                    # platenumber.append(a)
                    Carnumber = CarNumber()
                    Carnumber.carnumber=a
                    Carnumber.location = photo[11:]
                    Carnumber.locationnumber=parse.quote(photo[11:])
                    Carnumber.date = timezone.now()
                    Carnumber.save()

                    Tmpcarnumber=tmpcarnumber()
                    Tmpcarnumber.carnumber=a
                    Tmpcarnumber.location = photo[11:]
                    Tmpcarnumber.locationnumber=parse.quote(photo[11:])
                    Tmpcarnumber.date = timezone.now()
                    Tmpcarnumber.save() 
        if(photo[11:]!="static.PNG"):
            delete_s3Image(photo)  #s3에있는 이미지파일 삭제
        
    # Carnumber_all = CarNumber.objects.all()
    Carnumber_all = CarNumber.objects.filter(location__contains='서울특별시 서초구') 
    json = getjson_seocho()  
    context={
        'dataset':json,
        "Carnumber_all":Carnumber_all
    }

    return render(req, "index.html",context)

def uploadS3(cv_img,dst_info):  
        
    dstBucket,file_name =dst_info
    s3= boto3.resource('s3', 
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name='ap-northeast-2')  
    dstBucket = s3.Bucket(name='bucket0ryu')
    print(dstBucket)
    image_string = cv2.imencode('.jpg', cv_img)[1].tobytes() 
    dstBucket.put_object(Key = 'static/img/cropped_{}'.format(file_name), Body=image_string)
    

class PostDetailView(generic.DetailView):
    model = Post



def info(req):
    driver = Driver.objects.all()
    
    context={
        "driver": driver,
    }
    
    return render(req, "blog/info.html",context=context)


def search(req):
    driver = Driver.objects.all()
    q = req.POST.get('q',"")
    if q:
        driver = driver.filter(carnumbers__icontains=q)
        return render(req,'blog/info.html',{'driver':driver,'q':q})
    else:
        return render(req, 'blog/info.html')

def searchwhole(req):
    driver = Driver.objects.all()
    return render(req,'blog/info.html',{'driver':driver})


#문자 전송
def sendsns(req,phonenumber):
    # message = client.messages.create(
    # to = "+82"+f"{phonenumber}",
    # from_="+13194088767", 
    # body="문자 전송 Test")

    client = boto3.client(
    "sns",
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name="ap-northeast-1" 
    )

    topic_arn = 'arn:aws:sns:ap-northeast-1:919716432993:mysns'
    
    # client.subscribe(
    # TopicArn=topic_arn,
    # Protocol='sms',
    # Endpoint="+820"+f"{phonenumber}"
    # )
    
    # client.publish(
    # TopicArn=topic_arn ,
    # Message="헬맷 미착용이 감지되었습니다."
    # )
    client.publish(
    PhoneNumber="+820"+f"{phonenumber}",
    Message="헬맷 미착용이 감지되었습니다."
    )
    print("+820"+f"{phonenumber}")
    messages.success(req, '문자가 전송되었습니다.')
    Person = Driver.objects.filter(phonenumber__icontains=phonenumber)
    cnumber = Person[0]
    CarNumber.objects.filter(carnumber=cnumber).delete()


    return redirect("searchwhole")

def connect(req, carnumber):
    try:
        Person = Driver.objects.get(carnumbers=carnumber)
        phonenumber = Person.phonenumber

        client = boto3.client(
        "sns",
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name="ap-northeast-1" 
        )

        client.publish(
        PhoneNumber="+820"+f"{phonenumber}",
        Message="헬맷 미착용이 감지되었습니다."
        )
        messages.success(req, '문자가 전송되었습니다.')
        CarNumber.objects.filter(carnumber=carnumber).delete()

    except Driver.DoesNotExist:
        Person = None
        messages.error(req, '번호판에 맞는 운전자가 존재하지 않습니다.')
    return redirect('seocho')


def connect2(req, carnumber):
    try:
        Person = Driver.objects.get(carnumbers=carnumber)
        phonenumber = Person.phonenumber

        client = boto3.client(
        "sns",
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name="ap-northeast-1" 
        )
        topic_arn = 'arn:aws:sns:ap-northeast-1:919716432993:mysns'

        client.publish(
        PhoneNumber="+820"+f"{phonenumber}",
        Message="헬맷 미착용이 감지되었습니다."
        )
        
        messages.success(req, '문자가 전송되었습니다.')
        CarNumber.objects.filter(carnumber=carnumber).delete()

    except Driver.DoesNotExist:
        Person = None
        messages.error(req, '번호판에 맞는 운전자가 존재하지 않습니다.')

    return redirect('duckyang')

    


#s3에서 서버로 업로드
def upload():
    AWS_ACCESS_KEY_ID =os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY =os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = 'forstatic'
    AWS_REGION='ap-northeast-2'

    s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION)
    
    namelist = list()
    obj = s3.list_objects(Bucket=AWS_STORAGE_BUCKET_NAME)
    for content in obj['Contents']:
        if('static/img'in content['Key']):
            namelist.append(content['Key'])
    print("s3에서 업로드끝!")
    
    return namelist

# s3에 이미지 파일 삭제
def delete_s3Image(Photo):
    s3 = boto3.client('s3')
    s3.delete_object(Bucket="forstatic",Key=Photo)
    return


    
# 데이터시각화를 위해 json형식으로 바꾸기
def getjson_seocho():
    dataset = tmpcarnumber.objects \
        .filter(location__contains='서울특별시 서초구') \
        .values('date') \
        .annotate(cnt=Count('date')) \
        .order_by('date') 
    return dataset

def getjson_duckyang():
    dataset = tmpcarnumber.objects \
        .filter(location__contains='경기도 고양시 덕양구') \
        .values('date') \
        .annotate(cnt=Count('date')) \
        .order_by('date') 
    return dataset







#_googlevision_Function________________________________________________________________________

def config_env(srcBucket, file_name, dstBucket):
    configs=[]

    os. environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\kang4\\privateKey\\temporal-parser-329211-ce27c0f3eb53.json'
    client = vision.ImageAnnotatorClient()

    s3= boto3.resource('s3', 
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name='ap-northeast-2'
    )
    
    src_bucket = s3.Bucket(srcBucket) 
    img = src_bucket.Object('static/img/{}'.format(file_name)).get().get('Body').read()
    img_complete = cv2.imdecode(np.asarray(bytearray(img)),cv2.IMREAD_COLOR)
    
    dst_bucket = s3.Bucket(dstBucket)

    configs.append(client)                            ## Google Vision API 사용을 위한 Client 객체
    configs.append(CVToVision(img_complete,os.path.splitext(file_name)[1]))   ## google vision api 가 인식할 수 있도록 변환된 image (원본 이미지)
    configs.append(img_complete)                      ## OpenCV 가 인식할 수 있도록 변환된 image (원본 이미지)
    configs.append(list((dst_bucket,file_name)))      ## 번호판 사진을 저장할 Bucket 의 정보 (해당 목적지 Bucket 객체, 저장될 파일의 이름)

    return configs                                 

def getImgSize(cv_img):   
    h,w,c= cv_img.shape
    return h,w

def getPlateCoords(gpc_image,client,img_size):                        ## get Absolute Coords of plate if it exists, if failed 0 returned
    objects = client.object_localization(image=gpc_image).localized_object_annotations
    norm_coords = []

    for object_ in objects:
        if(object_.name == 'License plate'):   
            for vertex in object_.bounding_poly.normalized_vertices:
                norm_coords.append(tuple((vertex.x, vertex.y)))
    
    if not norm_coords:
        return -1

    Abs = []

    for coord in norm_coords:
        Abs.append(list([int(coord[0]*img_size[1]), int (coord[1]*img_size[0])]))
    return Abs

def getTextsCoords(gpc_image, client):
    response = client.text_detection(image=gpc_image)
    texts = response.text_annotations

    textCoords= []

    for text in texts:
        textCoords.append(tuple((text.description,[(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])))
    
    return textCoords

  

def CVToVision(cv_img,img_format):
    image = cv_img
    success, encoded_image = cv2.imencode(img_format, image)
    content2 = encoded_image.tobytes()
    image_cv2 = vision.Image(content=content2)
    return image_cv2

def Crop_Image(configs):
    client,gpc_image,cv_img,dst_info = configs
    img_prop= getImgSize(cv_img)
    
    Abs = getPlateCoords(gpc_image,client,img_prop)
    if(Abs == -1):
        print('No Plate Detected')
        return []

    print('Plate Detected Cropping Now')
    pts = np.array(Abs)
    
    ## (1) Crop the bounding rect
    poly_4 = cv2.boundingRect(pts)  
    x,y,w,h = poly_4
    croped = cv_img[y:y+h, x:x+w].copy()
    
    ## (2) make mask
    pts = pts - pts.min(axis=0)
    mask = np.zeros(croped.shape[:2], np.uint8)
    cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
    
    ## (3) do bit-op
    dst = cv2.bitwise_and(croped, croped, mask=mask)
    
    ## (4) add the white background
    bg = np.ones_like(croped, np.uint8)*255
    cv2.bitwise_not(bg,bg, mask=mask)
    dst2 = bg+ dst


    ## author BY Baek Geon Woo From KAU
    return dst2

#_____________________________________________________________________


# 웹캠 비디오스트리밍 코드
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@gzip.gzip_page
def detectme(request):
    try:
        cam = VideoCamera()
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:  # This is bad! replace it with proper handling
        print("에러입니다...")
        pass
# 여기까지 웹캠 코드

