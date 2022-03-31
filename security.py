from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
import time
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from twilio.rest import Client

pir = MotionSensor(4) 
camera = PiCamera()
camera.resolution = (640, 480)

SCOPES = ['https://www.googleapis.com/auth/drive'] #this scope lets you upload files to google drive
creds = Credentials.from_authorized_user_file('/path/to/folder/token.json', SCOPES)
drive_service = build('drive', 'v3', credentials=creds)
folder_id = 'folder_id' #"https://drive.google.com/drive/folders/[folder_id]"

twilio_sid = 'twilio_sid'
twilio_token = 'twilio_token' 
client = Client(twilio_sid, twilio_token)

while True:
    pir.wait_for_motion()
    #print('motion detected')
    
    now = datetime.now()
    now_string = now.strftime('%m-%d-%Y_%H-%M-%S')
    filename = 'video' + now_string + '.h264'
    camera.start_recording('/path/to/folder/videos/' + filename)
    #print('started recording')
    time.sleep(30) #record for 30 seconds
    camera.stop_recording()
    #print('stopped recording')
    
    file_metadata = {
        'name': filename, #the video's name on google drive
        'parents': [folder_id]
        }
    media = MediaFileUpload('/path/to/folder/videos/' + filename) #the name/path of video
    file = drive_service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    #print('video uploaded to google drive')

    client.messages \
        .create(
            body='the camera detected motion',
            from_='twilio_number', 
            to='your_number' 
    )
    #print('text sent')

    pir.wait_for_no_motion()
    