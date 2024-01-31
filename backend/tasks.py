import shutil
from app import celery, redis_client,bucket,logger
from urllib.parse import unquote, urljoin, quote,urlparse
import re
from pypdf import PdfWriter,PdfReader
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64
import zipfile
import os
import json
from celery import shared_task
import requests
import time
from google.api_core import exceptions
import pyminizip
from datetime import datetime



###### UTIL #####
def makedir(dirname):
    os.makedirs(dirname,exist_ok=True)
    return dirname
def delete_dir(dirname):
    if(os.path.exists(dirname)):
        shutil.rmtree(dirname)
def replace_case_insensitive(text, target, replacement):
    """
    Replace all case-insensitive occurrences of 'target' in 'text' with 'replacement'.
    """
    # This regular expression pattern means: 
    # - `re.escape(target)`: treat the 'target' string as a literal string, escaping any special characters.
    # - `flags=re.IGNORECASE`: make the search case-insensitive.
    pattern = re.compile(re.escape(target), flags=re.IGNORECASE)
    return pattern.sub(replacement, text)


###### SPLITING TASK ######

def extract_info_from_text(text):
    # Extracting name
    name_match = re.search(r'Magaca Saamilaha\s*[:\- ]*\s*([^\n]+)', text, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else None
    if name:
        # Replacing '/' or '\' in the name with '_'
        name = name.replace('/', '_').replace('\\', '_')

    # Extracting email (not matching a specific email)
    email_match = re.search(r'\b(?!Ileys2000@yahoo\.com\b)[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    email = email_match.group(0) if email_match else None

    return name, email

def upload_file_to_firebase(source_file_name, destination_blob_name,max_retries=5):
    
    blob = bucket.blob(destination_blob_name)

    for attempt in range(max_retries):
        try:
            blob.upload_from_filename(source_file_name)
            blob.make_public()
            print(f'Uploaded {source_file_name} to {destination_blob_name}')
            return blob.public_url
        except exceptions.GoogleAPICallError as e:
            if attempt < max_retries - 1:
                # Wait for 2^attempt seconds before retrying
                time.sleep(2**attempt)
            else:
                raise e

def download_file(url, destination):
    """
    Download a file from a given URL and save it to the specified destination.

    :param url: The URL of the file to download.
    :param destination: The path to save the downloaded file.
    """
    try:
    # Check if the request was successful
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=128):
                    file.write(chunk)
            print(f"File downloaded successfully and saved as {destination}")
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")
    except Exception as e:
        raise e
    



@shared_task(retry_backoff=3)   
def split_pdf_and_extract_info_task(file_url, mail_to_send,for_email=False):
    # Download file from Firebase Storage

    parsed_url = urlparse(file_url)
    path = parsed_url.path
    filename = os.path.basename(path)
    fname,extension = os.path.splitext(filename)

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    download_dir=makedir(f'./download/{timestamp}')
    downloaded_pdf=os.path.join(f'{download_dir}',f'{fname}{extension}')
    download_file(file_url,downloaded_pdf)


    sharelist = []
    def split_compress_send(page,  name, email=None):
        
        spilt_download_dir = makedir(f'./download/{timestamp}/split')

        writer = PdfWriter()
        writer.add_page(page)
        # writer.encrypt(os.environ.get('ENC_PASS'))
        with open(f'{spilt_download_dir}/{name}.pdf',"wb") as file:
            writer.write(file)

        # Create a unique filename for each split PDF
        # split_filename = f"split/{name}.pdf"
        # file_url = upload_file_to_firebase(f'{spilt_download_dir}/{name}.pdf', split_filename)
        
        send_message(mail_to_send,f'{spilt_download_dir}/{name}.pdf',name,email)
        sharelist.append({"name": name, "email": email, "local_path":f"./download/{timestamp}/split/{name}.pdf"})


    reader = PdfReader(downloaded_pdf)
    zip_dir_name = f'./download/{timestamp}/without emails' if for_email ==True else f'./download/{timestamp}/all'
    to_zip_dir = makedir(zip_dir_name)
    if(reader.is_encrypted):
        reader.decrypt(os.environ.get('ENC_PASS'))

    for page in reader.pages:
        text = page.extract_text()
        name, email = extract_info_from_text(text)
        if for_email:
            if name and email:
                split_compress_send(page, name, email)
            elif not email:
                writer = PdfWriter()
                writer.add_page(page)
                with open(f'{to_zip_dir}/{name}.pdf','wb') as f:
                    writer.write(f)
                    writer.close()

        else:
            if name:
                split_compress_send(page,name)
   
    

    zip_folder(to_zip_dir, f'{to_zip_dir}/zipped.zip', f'{os.environ.get("ENC_PASS")}')
   
    # zip_all_pdfs('',to_zip_dir,f'{to_zip_dir}/zipped.zip')
    if(os.path.exists(f'{to_zip_dir}/zipped.zip')):
        file_url = upload_file_to_firebase(f'{to_zip_dir}/zipped.zip','zipped')

    delete_dir('./download')
    redis_client.set('zip_link',file_url)
    return {"sharelist":sharelist,"zip_url":file_url}

###### EMAIL TASK ######

def create_message(sender, to, subject, message_text, file):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message['cc'] = "ndd@ileys.com, fc@ileys.com"
    

    msg = MIMEText(message_text)
    message.attach(msg)


    with open(file, 'rb') as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(file))
    part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
    message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def convert_path_to_url(local_path, base_url):
    # Convert the local path to URL path
    url_path = local_path.replace('.', '', 1) if local_path.startswith('./') else local_path

    # Ensure proper URL encoding
    url_path = quote(url_path)

    # Join the base URL with the encoded path
    return urljoin(base_url, url_path)


# @shared_task(retry_backoff=3)
def send_message(mail_to_send,file,name,email):

    credentials = Credentials(token=mail_to_send["access_token"], refresh_token=mail_to_send["refresh_token"])
    service = build('gmail','v1',credentials=credentials)
    
    
    replace_placeholder = replace_case_insensitive(mail_to_send["message"], '[magac]', name)
    # download_split_dir =  makedir('./download/split')
    # parsed_url = urlparse(to_send["firebase_path"])
    # path = parsed_url.path
    # filename = os.path.basename(path)
    # fname,extension = os.path.splitext(filename)
    # download_path = os.path.join(download_split_dir,f'{unquote(fname)}{extension}')
    # download_file(to_send["firebase_path"],download_path)

    # reader = PdfReader(download_path)
    # writer = PdfWriter()
    # if(reader.is_encrypted):
    #     reader.decrypt(os.environ.get('ENC_PASS'))
    # for page in reader.pages:
    #     writer.add_page(page)
    # with open(download_path,'wb') as unencrypted:
    #     writer.write(unencrypted)
    



    email_message = create_message(mail_to_send["from"],email,mail_to_send["subject"],replace_placeholder,file)
    send(service,'me',email_message)
    reader = PdfReader(file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(os.environ.get("ENC_PASS"))
    encrypted_dir = makedir('./download/enc')
    with open(f'{encrypted_dir}/{name}.pdf','wb') as f:
        writer.write(f)
    file_url = upload_file_to_firebase(os.path.join(encrypted_dir,f'{name}.pdf'),f'person/{name}')

    redis_client.lpush('all_emails',json.dumps({"name":name,"email":email,"path":file_url}))
    



def send(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print('An error occurred: %s' % error)

###### ZIPPING TASK ######

# @shared_task(retry_backoff=3)
def zip_all_pdfs(_,input_dir, output_file_name):
    with zipfile.ZipFile(output_file_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.pdf'):  # Filter for PDF files
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, input_dir))



def zip_folder(folder_path, zip_path, password):
    # List to store the paths of all the files to be compressed
    files_to_compress = []

    # Walk through the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Create complete filepath of file in directory
            file_path = os.path.join(root, file)
            # Add file to list
            files_to_compress.append(file_path)

    # Compress files
    compression_level = 5  # Compression level (1-9)
    if len(files_to_compress)==0:
        return
    pyminizip.compress_multiple(files_to_compress, [], zip_path, password, compression_level)


