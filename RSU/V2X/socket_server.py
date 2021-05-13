import socket, pickle
from datetime import datetime
import os.path
import csv


now = datetime.now()
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
count = 0
serv.bind(('192.168.1.3', 8080))
serv.listen(5)
csv_path = os.path.join('data/', 'rec_csv_file'+str(now)+'.csv')

print("Server started, running on port: 8080")
try:
	while True:
    		conn, addr = serv.accept()
		with open(csv_path, mode='w') as csv_file:
			csv_writer = csv.writer(csv_file, delimiter =',', quotechar='"', quoting= csv.QUOTE_MINIMAL)
			csv_writer.writerow(['countOBU','countRSU','latitude','longitude','Ax','Ay','Az','datetime','timeFromBeginning'])
    			while True:
				data = conn.recv(4096)
        			if not data:
	    				break
				countOBU,latitude,longitude,Ax,Ay,Az,datetime,timeFromBeginning = pickle.loads(data)
                                count+=1
				print('Server count:',count,'OBU count',countOBU)
        			print (countOBU,latitude,longitude,Ax,Ay,Az)
				csv_writer.writerow([countOBU,count,latitude,longitude,Ax,Ay,Az,datetime,timeFromBeginning])
        			conn.send("Hola dice  THE  SERVER<br>")
    			conn.close()
    	print 'client disconnected, sent packets: ' + str(count)
    	count=0
except KeyboardInterrupt:
	print("Server down")
