import streamlit as st
import torch
import cv2
import time
import sys
import telebot
from PIL import Image
import copy

TOKEN = '6985168300:AAGMtwb7wa1YfC5Ulc5xg1BmbONdvHmjer8'
chat_id = 916625140
@st.cache_resource
def load_bot():
	api_token = TOKEN
	bt = telebot.TeleBot(api_token)
	return bt 

bt = load_bot()

@st.cache_resource
def load_model():
	model = torch.hub.load('ultralytics/yolov5', 'custom', 
                      path='/Users/ivanpodoynikov/Jupyter/DLS/runs/train/exp/weights/best.pt')
	model.eval()
	return model

def on_update(count):
	data = count
	t.text(f'Amount of detections: {count}')

st.title("Face Detection App")
st.sidebar.title("Face Detection App") 
st.sidebar.title("Selection of camera") 
camera = st.sidebar.selectbox("From camera", ['None', 'Webcam'])
st.sidebar.text(f'{camera} is activated')
stframe = st.empty()
st.sidebar.title("Additions")
use_label = st.sidebar.checkbox('Label')
use_conf = st.sidebar.checkbox('Confidence')
amount = st.sidebar.checkbox('Count Detections')
finish = st.sidebar.button('Exit')
t = st.empty()

old_amount = -1
if finish:
	bt.send_message(chat_id, text = 'Finish Detecting')
	sys.exit(0)

if camera:
	if camera == 'Webcam':
		if amount: bt.send_message(chat_id, "Start Detecting with {}".format(camera) )
		model = load_model()

		cap = cv2.VideoCapture(0)
		frame_width = int(cap.get(3))
		frame_height = int(cap.get(4))

		while True:

			success, img = cap.read()
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			rgb_image = copy.copy(img)
			if success:

				results = model(img)
				df = results.pandas().xyxy[0]
				new_amount = df.shape[0]

				for ind in df.index:

					x1, y1 = int(df['xmin'][ind]), int(df['ymin'][ind])
					x2, y2 = int(df['xmax'][ind]), int(df['ymax'][ind])
					label = df['name'][ind]
					conf = "{:.2f}".format(df['confidence'][ind])

					cv2.rectangle(rgb_image, (x1, y1), (x2, y2), (255, 0, 255), 2)
					if use_label:
						cv2.putText(rgb_image, label, (x1, y1-5), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
					if use_conf:
						cv2.putText(rgb_image, conf, (x2, y1-5), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
						
				if amount == True:
					if new_amount != old_amount:
						old_amount = new_amount
						if new_amount > 0: 
							bt.send_message(chat_id, 'Someone is detected')
							bt.send_photo(chat_id, Image.fromarray(img))
						on_update(new_amount)

			stframe.image(rgb_image, use_column_width = True)