from picamera import PiCamera
from time import sleep
import time
#import paramiko


camera = PiCamera()


t = time.time()
camera.capture('/home/pi/Desktop/image.jpg')
t = time.time() - t

print(t)
#ssh= paramiko.SSHClient()
#ssh.connec('ip', username='pi', password='sudo')
#sftp = ssh.open_sftp()
#sftp.put(localpath, remotepath)
#sftp.close()
#ssh.close()