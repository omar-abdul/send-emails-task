from datetime import datetime, timedelta
from flask import Flask, request, jsonify,send_from_directory
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
import os
from celery import   chain
from celery.result import AsyncResult
import json
from flask_cors import CORS
import sentry_sdk
import firebase_admin
from firebase_admin import credentials,storage as firebase_storage
import base64
from pypdf import PdfReader, PdfWriter
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)




sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)






base_url = 'https://share-app-backend-blue-darkness-8568.fly.dev'
# base_url = 'https://localhost:5000'




def createapp():
    from extensions import make_celery, create_redis_client

  
    app = Flask(__name__)
    CORS(app)

    app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL')
    app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL')
    redis_client = create_redis_client()
    celery = make_celery(app)




    cred = credentials.Certificate(json.loads(base64.b64decode(os.environ.get('FIREBASE_ADMIN'))))
    firebase_admin.initialize_app(cred, {
    'storageBucket': 'share-app-842f8.appspot.com'
    })
  
    return app, redis_client,celery

# load_dotenv()

app,redis_client,celery= createapp()
bucket = firebase_storage.bucket()

def importTasks():
      from tasks import split_pdf_and_extract_info_task, send_message,zip_all_pdfs
      return split_pdf_and_extract_info_task,send_message,zip_all_pdfs


split_pdf_and_extract_info_task,send_message,zip_all_pdfs = importTasks()




def get_all_email_data(redis_client):
    keys = redis_client.lrange('all_emails', 0, -1)  # Get all keys from the list

    all_data = [json.loads(item) for item in keys]


    return all_data



def get_user_email(access_token):
    # Google endpoint for user info
    url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    # Include the access token in the Authorization header
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return user_info.get("email")  # Extract the email
    else:
        print(f"Failed to fetch user info: {response.status_code}")
        return None

redirect_uri = os.environ.get('REDIRECT_URI')
# redirect_uri='https://shareapp.pages.dev/auth/callback'

@app.route("/",methods=['GET'])
def hello():
    return 'hello world '+os.environ.get('REDIS_HOST')

@app.route('/exchange-token',methods=['POST'])
def exchange_token():
    code = request.json.get('code')
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': os.environ.get("CLIENT_ID"),
        'client_secret': os.environ.get('CLIENT_SECRET'),
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    })
 

    return response.json()

@app.route('/send-emails',methods=["POST"])
def send_emails():

    redis_client.delete('all_emails')
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"})
    token = auth_header.split(" ")[1]
    if(not get_user_email(token)):
        return jsonify({"error": "Unauthorized"})


    refreshToken = request.form.get('refresh_token')



    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        blob = firebase_storage.bucket().blob(filename)
        reader = PdfReader(file)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(os.environ.get('ENC_PASS'),algorithm="AES-256")
        from tasks import makedir
        makedir('./download')
        with open('./download/initial.pdf','wb') as f:
            writer.write(f)
        try:

            blob.upload_from_filename('./download/initial.pdf')
            blob.make_public()
            file_url = blob.public_url
        except Exception as e:
            logger.error(f'There was an error: ${e}')


    subject = request.form.get('subject')
    message = request.form.get('message')
    mail_send = {"from": get_user_email(token),'subject':subject,'message':message,"access_token":token,"refresh_token":refreshToken}

    task_chain = split_pdf_and_extract_info_task.delay(file_url,mail_send,for_email=True)

   
    if(task_chain.status=="PENDING"):
        logger.info(f'Task began with id {task_chain.id}')
        return jsonify({"success":True,'task_id':task_chain.id})
    elif(task_chain.failure()):
        logger.error(f'ERROR WITH TASK {task_chain.id} :- {task_chain.result}')
        return jsonify({"success":False})



@app.route('/email/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    auth_header = request.headers.get('Authorization')  
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"})
   
    
    task_result = AsyncResult(task_id,app=celery)

    status = task_result.status
    if(task_result.status =='FAILURE' or task_result.failed() or (task_result.ready() and task_result.status !="SUCCESS")):
        exception = task_result.result
        logger.error(f'ERROR : {exception}')
        return jsonify({"status":"failure","emails":[],"message":"There was an internal error"})

    email_sent = get_all_email_data(redis_client)
    zip_link_encoded = redis_client.get('zip_link')
    zip_link=zip_link_encoded.decode('utf8') if(zip_link_encoded)else ''
    if(status=='PENDING' or status=='SUCCESS'):
        return jsonify({"status": status,"emails":email_sent,"zip_link":zip_link})
        





if __name__ == '__main__':
    app.run()