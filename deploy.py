### importing required libraries
import torch
import cv2
import time
import re
import numpy as np
import easyocr
import serial

##### DEFINING GLOBAL VARIABLE
EASY_OCR = easyocr.Reader(['en'], gpu=True) ### initiating easyocr
OCR_TH = 0.2
# NAMA_RUANGAN = str(input('Nama Ruangan : '))
# NAMA_RUANGAN = NAMA_RUANGAN.upper()

ArduinoSerial = serial.Serial('/dev/ttyACM0',9600,timeout=0.1)

### -------------------------------------- function to run detection ---------------------------------------------------------
def detectx (frame, model):
	frame = [frame]
	print(f"[INFO] Detecting. . . ")
	results = model(frame)
	labels, cordinates = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]

	return labels, cordinates

#### ---------------------------- function to recognize license plate --------------------------------------


# function to recognize license plate numbers using Tesseract OCR
def filter_text(region, ocr_result, region_threshold):
	rectangle_size = region.shape[0]*region.shape[1]
	
	plate = [] 
	for result in ocr_result:
		length = np.sum(np.subtract(result[0][1], result[0][0]))
		height = np.sum(np.subtract(result[0][2], result[0][1]))
		
		if length*height / rectangle_size > region_threshold:
			plate.append(result[1])
	return plate


def recognize_plate_easyocr(img, coords,reader,region_threshold):
	# separate coordinates from box
	xmin, ymin, xmax, ymax = coords
	nplate = img[int(ymin):int(ymax), int(xmin):int(xmax)] ### cropping the number plate from the whole image
	ocr_result = reader.readtext(nplate)
	text = filter_text(region=nplate, ocr_result=ocr_result, region_threshold= region_threshold)

	if len(text) ==1:
		text = text[0].upper()
	return text, ocr_result


### to filter out wrong detections 



### ------------------------------------ to plot the BBox and results --------------------------------------------------------
def plot_boxes(results,frame,classes):

	"""
	--> This function takes results, frame and classes
	--> results: contains labels and coordinates predicted by model on the given frame
	--> classes: contains the strting labels
	"""
	global plate_num
	global bbox_area
	labels, cord = results
	n = len(labels)
	x_shape, y_shape = frame.shape[1], frame.shape[0]
	print(f"[INFO] Total {n} detections. . . ")
	print(f"[INFO] Looping through all detections. . . ")


	### looping through the detections
	for i in range(n):
		row = cord[i]
		if row[4] >= 0.55: ### threshold value for detection. We are discarding everything below this value
			print(f"[INFO] Extracting BBox coordinates. . . ")
			x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape) ## BBOx coordniates
			text_d = classes[int(labels[i])]

			coords = [x1,y1,x2,y2]
			bbox_area  = (x2-x1)*(y2-y1) 
			text, plate_num = recognize_plate_easyocr(img = frame, coords= coords, reader= EASY_OCR, region_threshold= OCR_TH)

			cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) ## BBox
			cv2.rectangle(frame, (x1, y1-20), (x2, y1), (0, 255,0), -1) ## for text label background
			if plate_num != []:
				cv2.putText(frame, f"{plate_num[0][1]}", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255), 2)
				return frame, plate_num, bbox_area
			
	return frame, [(0, 0, 0)] ,0
### ---------------------------------------------- Main function -----------------------------------------------------

def main(img_path=None, vid_path=None, vid_out = None):
	string = ''
	print(f"[INFO] Loading model... ")
	## loading the custom trained model
	model =  torch.hub.load('./yolov5', 'custom', source ='local', path='best.pt',force_reload=True) ### The repo is stored locally

	classes = model.names ### class names in string format

	### --------------- for detection on video --------------------
	if vid_path !=None:
		print(f"[INFO] Working with video: {vid_path}")

		## reading the video
		cap = cv2.VideoCapture(vid_path)

		width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		fps = int(cap.get(cv2.CAP_PROP_FPS))

		frame_no = 1

		cv2.namedWindow("vid_out", cv2.WINDOW_NORMAL)
		while True:
			# start_time = time.time()
			ret, frame = cap.read()
			if ret  and frame_no %1 == 0:
				print(f"[INFO] Working with frame {frame_no} ")

				frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

				results = detectx(frame, model = model)
				frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
				frame, num_plate, area_bbox = plot_boxes(results, frame, classes=classes)
				print(f'[INFO] Character Result : {num_plate[0][1]}')
				print(f'[INFO] Area : {area_bbox}')
				if area_bbox < 5000:
					string = '3'
				elif area_bbox >= 5000:
					string = '0'

				print('--------------------------------------------------------------------------------')				
				cv2.imshow("vid_out", frame)
				ArduinoSerial.write(bytes(string, 'utf-8'))
				print('[INFO] PWM Value :',ArduinoSerial.readline().decode('utf-8'))
		
				if cv2.waitKey(5) & 0xFF == ord('q'):
					cv2.imwrite('final_output/video_to_image_capture.jpg',frame)
					break
				frame_no += 1
		
		print(f"[INFO] Cleaning up. . . ")
		cv2.destroyAllWindows()



### -------------------  calling the main function-------------------------------


main(vid_path="./test_footages/output3.mp4") ### for custom video
# main(vid_path=0) #### for webcam