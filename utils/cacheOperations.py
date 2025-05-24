import boto3
from dotenv import load_dotenv
import os
import json

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

s3 = boto3.client('s3', aws_access_key_id = AWS_ACCESS_KEY, aws_secret_access_key = AWS_SECRET_KEY)
cache_bucket = "cache-bucket-sheshya"

def check_hit(folder_name, file_name):
    try:
        response = s3.get_object(Bucket = cache_bucket, Key = f"{folder_name}/{file_name}")
        data = json.loads(response['Body'].read())
        
        return data
    except Exception as e:
        print(f"Error checking key existence: {e}")
        return None


def store_obj(folder_name, file_path, obj):
    print(obj)
    try:
        ret = s3.put_object(Bucket = cache_bucket, Key = f"{folder_name}/{file_path}", Body = json.dumps(obj))
        print(ret)
        return True
    except Exception as e:
        print(e)
        return False
    


def process_call(userId, folder_name, kv_dict, file_name = None):
    file_path = ""
    
    if file_name:
        file_path = file_name
    else:
        file_path = f"{userId}_file"
    hit_obj = check_hit(userId, folder_name, file_path)
    
    if hit_obj:
        print("found hit")
        if hit_obj['hits'][userId]:
            return hit_obj['hits'][userId]
        else:
            ret = store_obj(userId, folder_name, hit_obj, file_path)
            print('response storing: ', ret)
            return False
    else:
        print("storing fresh")
        ret = store_obj(userId, folder_name, None, kv_dict, file_path)
        print("response storing: ", ret)
        return False
    

# rsp = check_hit("", "imageCache", "12345abc.txt")
# print(rsp)

# rsp = process_call("12345abc", "imageCache", {"ref_id": "check123", "url": "someurl.com", "imageName": "check image"}, "check123")
# print(rsp)