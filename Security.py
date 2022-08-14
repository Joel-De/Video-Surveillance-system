import cv2
import serial
import time
from Predictor import DetectImg
from Server import SQLDataBase
from datetime import datetime
from multiprocessing import Process, Queue


###         Processes           ###
def MoveToDB(InstanceBuffer):
    DB = SQLDataBase("DataStorageContainer.db")
    tableNames = DB.getTableList()
    tableNames = [int(name[2:]) for name in tableNames]
    TableID = (max(tableNames) + 1) if (len(tableNames) > 0) else 0
    DB.CreateTable('ID' + str(TableID))
    for image in InstanceBuffer:
        Today = datetime.today()
        Time = Today.strftime('%H:%M:%S')
        Date = Today.strftime('%d/%m/%Y')
        ImageEncoded = cv2.imencode('.png', image)[1].tobytes()
        DB.AddEntry('ID' + str(TableID), Date, Time, 1, ImageEncoded)
    DB.connection.close()
    print("[LOG] Data Transfer Complete")


def ReadImage(queue, ImgSize):
    Camera = cv2.VideoCapture(0)
    Camera.set(3, ImgSize[0])
    Camera.set(4, ImgSize[1])
    while True:
        _, img = Camera.read()
        queue.put(img)
        time.sleep(0.05)


##############################################


###         Queue           ###

def emptyQueue(ImgQueue):
    for i in range(ImgQueue.qsize()):
        ImgQueue.get()


def copyQueue(ImgQueue):
    listOfImages = []
    for i in range(ImgQueue.qsize()):
        listOfImages.append(ImgQueue.get())
    return listOfImages


##############################################


###         SerialInterface           ###

def SendCommand(command):
    arduino.write(bytes(command, 'utf-8'))
    Confirmation = arduino.readline()
    while (Confirmation.decode('UTF-8')) != '1':
        Confirmation = arduino.readline()
        time.sleep(0.015)


##############################################


if __name__ == '__main__':

    OffsetThresh = 0.3  # Percentage of deviance from object to center in order to rotate gimbal
    ImgSize = (1280, 720)  # Size of Video Input
    InstanceThreshold = 5  # Number of Seconds between video instances to be the same
    ModelDir = "Models/model_27.pth"
    ArduinoComPort = 'COM4'

    arduino = serial.Serial(port=ArduinoComPort, baudrate=19200, timeout=.1, writeTimeout=1)
    time.sleep(3)

    predictor = DetectImg(ModelDir)

    ImgQueue = Queue(maxsize=-1)
    proc = Process(target=ReadImage, args=[ImgQueue, ImgSize])
    proc.start()

    InstanceStart = 0
    InstanceBuffer = []
    Recording = False

    SendCommand("VM50")  # Raises Camera to level height
    print("[LOG] Started")
    while True:

        imgOriginal = ImgQueue.get()
        boxes = predictor.Predict(imgOriginal)

        if ((
                    time.time() - InstanceStart) > InstanceThreshold) and Recording:  # Check to see if detection instance has passed threshold and saves to database
            print("[LOG] Starting Data Transfer Process")
            Recording = False
            MoveThread = Process(target=MoveToDB, args=[InstanceBuffer.copy()])
            MoveThread.start()
            InstanceBuffer = []

        if len(boxes) == 0:  # Checks to see if any detections were made, if not exits loop

            if not Recording:
                emptyQueue(ImgQueue)
            continue

        if (time.time() - InstanceStart) < InstanceThreshold:
            InstanceBuffer += copyQueue(ImgQueue)
            InstanceStart = time.time()

        else:
            InstanceStart = time.time()
            print("[LOG] Starting Recording")

            Recording = True
            InstanceBuffer += copyQueue(ImgQueue)

        avg = None

        for box in boxes:
            if avg is None:
                avg = [0, 0]
            avg[0] += (box[1][0] + box[0][0]) / 2
            avg[1] += (box[1][1] + box[0][1]) / 2
            cv2.rectangle(imgOriginal, box[0], box[1], (220, 0, 0), 3)

        avg[0] = round(avg[0] / len(boxes))
        avg[1] = round(avg[1] / len(boxes))
        value = abs(((ImgSize[0] / 2) - avg[0]) / OffsetThresh)

        Thresh = (((ImgSize[0] / 2) - avg[0]) / (ImgSize[0] / 2))
        Angle = str(round(4.5 * (1 / Thresh)))

        if Thresh > OffsetThresh:
            SendCommand("HN" + Angle)

        elif (-1) * Thresh > OffsetThresh:
            SendCommand("HN" + Angle)

        # if ((ImgSize[1] / 2) - avg[1]) < OffsetThresh:
        #     Vertical.nudge(5)
        #
        # elif ((ImgSize[1] / 2) - avg[1]) > OffsetThresh:
        #     Vertical.nudge(-5)
