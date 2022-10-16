import datetime

from rest_framework.permissions import IsAuthenticated
from time import sleep

from django.views.decorators import gzip
from django.http import StreamingHttpResponse, HttpResponse
import cv2
import threading
import time
from django.utils import timezone
from queue import Queue, PriorityQueue

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from main_app.models import Frame, Rock

processed_frame_dict = PriorityQueue(maxsize=100)
Q_id = Queue(maxsize=100)
DELETE_OLD_FRAMES = False
FPS = 3


class FileVideoStream:
    def __init__(self, path):
        self.stream = cv2.VideoCapture(path)
        # self.stream = cv2.VideoCapture('http://localhost:8000/api/app/test3')
        self.stopped = False
        self.frame_counter = 1
        self.frame_id = 0
        self.previous_frame = None

    def start(self):
        t = threading.Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        global Q_id
        global DELETE_OLD_FRAMES
        global FPS

        while True:
            start_time = time.time()
            if self.stopped:
                return

            (grabbed, frame) = self.stream.read()
            self.frame_counter += 1
            if self.frame_counter % (30//FPS) != 0:
                continue
            self.frame_id += 1
            if not grabbed:  # TODO: start video again if it ends
                self.stop()
                return
            # print(self.frame_id)

            t = threading.Thread(target=self.store_frame, args=(frame, self.frame_id))
            t.start()
            if Q_id.qsize() >= 100 and DELETE_OLD_FRAMES:
                Q_id.get()

            delay = 0.050
            if time.time() - start_time < delay:
                sleep(delay - (time.time() - start_time))

    def store_frame(self, *args):
        cv2.imwrite(f"../frames/{args[1]}.jpg", args[0])
        Q_id.put(args[1])

    def stop(self):
        self.stopped = True

    def get_latest_frame(self):
        global processed_frame_dict
        # print(processed_frame_dict.queue)
        # return processed_frame_dict.get(max(processed_frame_dict.keys()))
        if not processed_frame_dict.empty():
            print('Success')
            self.previous_frame = processed_frame_dict.get()
            # processed_frame_dict.put((1, temp))

            return self.previous_frame
        elif self.previous_frame is not None:
            print('Return previous frame')
            return self.previous_frame
        else:
            print('Zero frames were processed')
            return None


fvs = FileVideoStream('../media/lol.mp4').start()


@gzip.gzip_page
def Main(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    global fvs
    sleep(0.5)
    return StreamingHttpResponse(gen(fvs), content_type="multipart/x-mixed-replace;boundary=frame")


class FrameView(APIView):

    def get(self, request):
        global Q_id
        if not Q_id.empty():
            frame_id = Q_id.get()
            print(f"sent to ml frame with id: {frame_id}")
            with open('oversize.txt', 'r') as r:
                oversize = int(r.readline().strip())
            return Response(data={'id': frame_id, 'min_mm': oversize}, status=status.HTTP_200_OK)
        else:
            return Response(data={'id': 0, 'min_mm': 0}, status=status.HTTP_200_OK)

    def post(self, request):
        global processed_frame_dict
        # print(processed_frame_dict.queue)
        frame_id = int(request.data.get('id'))
        print(f"get from ml frame with id: {frame_id}")
        image = cv2.imread(f"../frames/{frame_id}.jpg")
        _, jpeg = cv2.imencode('.jpg', image)
        temp = jpeg.tobytes()
        frame = request.data.get('bboxes')
        frame_obj = Frame.objects.create(timestamp=timezone.now(), fullness=request.data.get('fullness'))
        for i in frame:
            Rock.objects.create(max_size=max(i.get('height'), i.get('width')), frame=frame_obj)
        processed_frame_dict.put((frame_id, temp))
        print('test1', processed_frame_dict.queue[0][0])
        return Response(status=status.HTTP_200_OK)


def gen(camera):
    while True:
        start_time = time.time()
        frame = camera.get_latest_frame()
        delay = 1 / FPS
        if time.time() - start_time < delay:
            sleep(delay - (time.time() - start_time))
        else:
            print(f"Delay was too long in get ( > {delay})")
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame[1] + b'\r\n\r\n')
        else:
            yield


class Statistics(APIView):
    """ Return statistics. """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            oversize = int(request.query_params.get('oversize'))
        except (TypeError, ValueError):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': "'oversize' was not provided or is not valid."
            })
        f = open('oversize.txt', 'w')
        f.write(str(oversize))
        f.close()
        start_timestamp = (timezone.now() - datetime.timedelta(days=7))
        recent_frames = Frame.objects.filter(timestamp__gt=start_timestamp).order_by('-id')[:50][::-1]
        frames = Frame.objects.filter(timestamp__gt=start_timestamp).filter(rock__max_size__gte=oversize).order_by('timestamp').distinct().order_by('-id')[:100][::-1]
        amount_frames_with_oversize = Frame.objects.filter(timestamp__gt=(timezone.now() - datetime.timedelta(seconds=1))).filter(rock__max_size__gte=oversize).count()
        rocks = Rock.objects.all().filter(frame__timestamp__gt=(timezone.now() - datetime.timedelta(minutes=10)))
        amount_of_rocks = rocks.count()
        classes = {
            'class_1_amount': rocks.filter(max_size__gt=0).filter(max_size__lte=request.query_params.get('class_1')).count(),
            'class_2_amount': rocks.filter(max_size__gt=request.query_params.get('class_1')).filter(max_size__lte=request.query_params.get('class_2')).count(),
            'class_3_amount': rocks.filter(max_size__gt=request.query_params.get('class_2')).filter(max_size__lte=request.query_params.get('class_3')).count(),
            'class_4_amount': rocks.filter(max_size__gt=request.query_params.get('class_3')).filter(max_size__lte=request.query_params.get('class_4')).count(),
            'class_5_amount': rocks.filter(max_size__gt=request.query_params.get('class_4')).filter(max_size__lte=request.query_params.get('class_5')).count(),
            'class_6_amount': rocks.filter(max_size__gt=request.query_params.get('class_5')).filter(max_size__lte=request.query_params.get('class_6')).count(),
            'class_7_amount': rocks.filter(max_size__gt=request.query_params.get('class_6')).filter(max_size__lte=request.query_params.get('class_7')).count()
        }
        if amount_of_rocks > 0:
            classes['class_1_percent'] = "{:.2f}".format(classes.get('class_1_amount') / amount_of_rocks)
            classes['class_2_percent'] = "{:.2f}".format(classes.get('class_2_amount') / amount_of_rocks)
            classes['class_3_percent'] = "{:.2f}".format(classes.get('class_3_amount') / amount_of_rocks)
            classes['class_4_percent'] = "{:.2f}".format(classes.get('class_4_amount') / amount_of_rocks)
            classes['class_5_percent'] = "{:.2f}".format(classes.get('class_5_amount') / amount_of_rocks)
            classes['class_6_percent'] = "{:.2f}".format(classes.get('class_6_amount') / amount_of_rocks)
            classes['class_7_percent'] = "{:.2f}".format(classes.get('class_7_amount') / amount_of_rocks)
        else:
            classes['class_1_percent'] = 0
            classes['class_2_percent'] = 0
            classes['class_3_percent'] = 0
            classes['class_4_percent'] = 0
            classes['class_5_percent'] = 0
            classes['class_6_percent'] = 0
            classes['class_7_percent'] = 0
        return Response(status=status.HTTP_200_OK, data={
            'data': [
                {
                    'timestamp': frame.timestamp,
                    'min_oversize': frame.rock.latest('max_size').max_size,
                    'max_oversize': frame.rock.filter(max_size__gt=oversize).earliest('max_size').max_size,
                    'amount': frame.rock.filter(max_size__gt=oversize).count(),
                } for frame in frames
            ],
            'fullness': [{'value': "{:.2f}".format(frame.fullness), 'timestamp': frame.timestamp} for frame in recent_frames],
            'is_oversize': amount_frames_with_oversize > 0,
            'class_data': classes
        })
