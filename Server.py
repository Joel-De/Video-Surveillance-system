import cv2
import numpy as np
import os
import sqlite3
from sqlite3 import Error


class SQLDataBase():

    def __init__(self, DBPath):
        self.connection = None
        try:
            self.connection = sqlite3.connect(DBPath)
            print("[LOG] Connection to SQLite DB successful")
        except Error as e:
            print("[LOG] " + e)
            quit()

    def CreateTable(self, TableName):
        cursor = self.connection.cursor()
        createtable = "CREATE TABLE IF NOT EXISTS " + TableName + " (Date text , Time text, Camera int, Image blob );"
        cursor.execute(createtable)

    def AddEntry(self, TableID, Date, Time, CameraID, Image):
        script = "INSERT INTO " + TableID + " (Date, Time, Camera, Image) VALUES (?, ?, ?, ?);"
        cursor = self.connection.cursor()
        cursor.execute(script, (Date, Time, CameraID, Image))
        self.connection.commit()

    def getTableList(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        rows = cursor.fetchall()
        rows = [row[0] for row in rows]
        return rows

    def getEntry(self, TableID):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM " + TableID)
        rows = cursor.fetchall()
        return rows


if __name__ == '__main__':

    db = SQLDataBase('DataStorageContainer.db')
    outfolder = "VideoOutput"

    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    tableList = db.getTableList()
    for table in tableList:
        rows = db.getEntry(table)
        timestamp = (str(rows[0][0]) + " " + str(rows[0][1])).replace('/', '_').replace(':', '_')
        print("[LOG] READING ENTRY " + timestamp)

        VideoWrite = cv2.VideoWriter_fourcc(*'mp4v')
        fname = os.path.join(outfolder, str(timestamp + '.mp4'))
        out = cv2.VideoWriter(fname, VideoWrite, 10.0, (1280, 720))

        for row in rows:
            nparr = np.frombuffer(row[3], np.uint8)
            converted = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            timestamp = str(row[0]) + " " + str(row[1])
            converted = cv2.putText(converted, timestamp, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 0, 255), 2, cv2.LINE_AA)

            out.write(converted)
