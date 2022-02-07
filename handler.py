from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
from pathlib import Path
import requests
import boto3
import string, random
import json

# Function to return output in JSON format
def get_json(status_code, data):
    response = {
        "statusCode": status_code,
        "headers": {},
        "body": json.dumps(data)
    }
    return response

# Function to download the videos from a URL
def download_file(url):
    local_filename = '/'.join([ "/tmp/source", url.split('/')[-1]])
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename  


# Function to merge two videos
def video_concatenate(video_list, output):
    concatenated = concatenate_videoclips(video_list)
    #temp_audiofile_path parameter needed, because for creating temp audio file for the videos
    concatenated.write_videofile(output, codec='libx264', temp_audiofile_path="/tmp")
    return

# Function to upload completed video to S3 bucket
def video_upload(video):
    import os

    output_bucket = os.getenv("BUCKET")
    upload_filename = '/'.join([ "preview_uploads", video.split('/')[-1]])
    
    client = boto3.client('s3')
    try:
        response = client.upload_file(video, output_bucket, upload_filename)
        print(response)
    except Exception as e:
        return e

# Function to create a random string
def id_generator(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Main Function
def lambda_function(event, context):
    #Get urls as a list from event
    urls = event['urls']
    
    # Create directories for storing files and outputs
    Path('/tmp/source').mkdir(parents=True, exist_ok=True)
    Path('/tmp/preview_uploads').mkdir(parents=True, exist_ok=True)
    
    # Downloading file from URLS
    for url in urls:
        input_file = download_file(url)

    # Reading input videos for splitting from source directory
    input = Path('/tmp/source').glob('**/*.mp4')

    # Get filename path
    videos = [ x.as_posix() for x in input if x.is_file()]
    videos_out_landscape = []
    videos_out_portrait = []

    random_name = id_generator()

    # Processing videos
    for video in videos:
        # Get the first 2 seconds of a video
        video = VideoFileClip(video).subclip(0, 2)
        # Checking if video is landscape or portrait and creating separate lists
        if video.size == (1080, 1920):
            videos_out_portrait.append(video)
        else:
            videos_out_landscape.append(video)
            
    # Checking if videos are available before concatenating. Empty lists throws error
    if not len(videos_out_landscape) == 0:
        video_concatenate(videos_out_landscape, "/tmp/preview_uploads"+random_name+"_landscape.mp4")
    if not len(videos_out_portrait) == 0:
        video_concatenate(videos_out_portrait, "/tmp/preview_uploads/"+random_name+"_portrait.mp4")

    # Reading list of output files for upload
    out_files = Path('/tmp/preview_uploads').glob('**/*.mp4')
    out_files_list = [ x.as_posix() for x in out_files if x.is_file()]

    # Uploading them
    for out in out_files_list:
        video_upload(out)
    
    # Returning output message
    return get_json(200, "Preview generated and uploaded")


######### TEST EVENT #########################
#{
#    "urls": [
#        video-url-1,
#        video-url-2,
#    ]
#}
###############################################