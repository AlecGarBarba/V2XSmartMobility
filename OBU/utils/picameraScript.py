from picamera import PiCamera
import time
from paramiko import SSHClient
from scp import SCPClient


camera = PiCamera()

camera.capture('/home/pi/Desktop/image.jpg')

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect('raspberrypi1')

scp = SCPClient(ssh.get_transport())

scp.put('image.jpg', remote_path='/home/pi/Desktop');