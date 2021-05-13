import serial
import time
import string
import pynmea2
import smbus
import socket, pickle
from datetime import datetime
import csv
import sys
import os.path
from picamera import PiCamera
from paramiko import SSHClient
from scp import SCPClient


#Global variables
count =0 #max of 1000 packets per experiment

#accelerometer registers
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

#GPS variables


#camera init
camera = PiCamera()
ssh = SSHClient()
ssh.load_system_host_keys()

#Socket implementation
SERIAL_PORT="/dev/ttyAMA0"
running = True
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.1.3',8080 ))
print("connection established")

def MPU6050_Init():
	bus.write_byte_data(MPU6050_Register_Address, SMPLRT_DIV, 7)
	bus.write_byte_data(MPU6050_Register_Address, PWR_MGMT_1, 1)
	bus.write_byte_data(MPU6050_Register_Address, CONFIG, 0)
	bus.write_byte_data(MPU6050_Register_Address, GYRO_CONFIG, 24)
	bus.write_byte_data(MPU6050_Register_Address, INT_ENABLE, 1)

def get_acceleration_data():
	acc_x = read_raw_data(ACCEL_XOUT_H)
	acc_y = read_raw_data(ACCEL_YOUT_H)
	acc_z = read_raw_data(ACCEL_ZOUT_H)
	Ax = acc_x/16384.0
	Ay = acc_y/16384.0
	Az = acc_z/16384.0
	return (str(Ax),str(Ay),str(Az))

def read_raw_data(addr):
    high = bus.read_byte_data(MPU6050_Register_Address, addr)
    low = bus.read_byte_data(MPU6050_Register_Address, addr+1)
    value = ((high << 8) | low)
    if(value > 32768):
            value = value - 65536
    return value

def sendSnapshot():
    global now, ssh
    localPath ='/home/pi/Desktop/OBU_folder/images/image'+str(now)+'.jpg'
    camera.capture(localPath)
    print("establishing connection")
    ssh.connect('raspberrypi1')
    scp = SCPClient(ssh.get_transport())
    print("conn established")
    scp.put(localPath, remote_path='/home/pi/Desktop/RSU_folder/images/')
    
    
    
    
def getPositionData(gps):
    global count
    global file
    global now
    
    data = gps.readline()
    message = data[0:6]
    
    if (message == "$GPRMC"):
        # GPRMC = Recommended minimum specific GPS/Transit data
        parts = data.split(",")
        newmsg=pynmea2.parse(data)
        latit= newmsg.latitude
        lng = newmsg.longitude
        print("latitude: " + str(latit) +  " longitude:  " + str(lng) )
        #client.send("latitude: " + str(latit) +  " longitude:  " + str(lng) + "   time:  "+ str(datetime.now() - now) + "\n" )
        #from_server = client.recv(4096)
        
        if parts[2] == 'V':
            # V = Warning, most likely, there are no satellites in view...
            print "GPS receiver warning, no signal"
        return(str(latit), str(lng))
    return(None,None)

def sendSensorData(count,latitude,longitude,Ax,Ay,Az,datetime,time):
    dataToSend = ([str(count),latitude,longitude,Ax,Ay,Az,datetime,time])
    data_string = pickle.dumps(dataToSend)
    client.send(data_string)
    from_server = client.recv(4096)

###Start of the application

print "Application started!"
gps = serial.Serial(SERIAL_PORT, baudrate = 9600, timeout = 0.5)
now = datetime.now()
bus = smbus.SMBus(1) 
MPU6050_Register_Address = 0x68 
MPU6050_Init()
csv_path = os.path.join('data/', 'sent_csv_file'+str(now)+'.csv') 

with open(csv_path, mode='w') as csv_file:
    csv_writer = csv.writer(csv_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['count','latitude','longitude','Ax','Ay','Az', 'datetime', 'timeFromBeginning'])
    while running:
        try:
            latitude, longitude = getPositionData(gps)
            Ax,Ay,Az = get_acceleration_data()
            if(latitude != None):
                count += 1
                csv_writer.writerow([count,latitude,longitude,Ax,Ay,Az,str(datetime.now()),str(datetime.now() - now)])
                sendSensorData(count,latitude,longitude,Ax,Ay,Az,str(datetime.now()), str(datetime.now() - now)  )
                
            	if(count%10 == 0):
                	try:
                    		sendSnapshot()
                    		a = 1
                	except Exception as e:
                    		print("image could not be sent. ", e)
            if(count > 1000): running = False
        except KeyboardInterrupt:
            running = False
           # client.close()
            gps.close()
            print "sent packets: " + str(count)
            print "Application closed!"
        except Exception as e:
            # You should do some error handling here...
            print ("Application error! ", e)


#client.close()
gps.close()
print "sent packets: " + str(count)
