import linkedInJobs.search as linkedin
import naukriJobs.search as naukri
from utils import llmCaller as call
from utils import json_parser as jp
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import boto3
from io import BytesIO
import os
import datetime
import hashlib
import re
import json
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv("API_KEY_ID")
aws_secret_access_key = os.getenv("API_SECRET_KEY")


def _hashString(user_query):
    return hashlib.md5(user_query.encode()).hexdigest()

def _store_to_s3(name, df : pd.DataFrame):
    s3 = boto3.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name = "ap-south-1")
    buffer = BytesIO()
    
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    s3_key = f"{name}.xlsx"
    s3_key = f"jobAgent/{name}.xlsx"
    s3.upload_fileobj(
        buffer,
        "resume-store-hiremeclub",
        s3_key,
        # ExtraArgs={'ACL': 'public-read'}
    )

    url = f"https://resume-store-hiremeclub.s3.ap-south-1.amazonaws.com/{s3_key}"
    return url

def _validate_query(query):
    prompt = f"""
    You are given with the user query you have to check if the query is intended for job search or not.
    If the query is intended for job search then return True else return False.

    Give output in the following JSON format:
    {{
        "isJobSearch": <True/False>,
        "query": "<user query>"
    }}

    Now check the following user query:
    {query}
    """
    response = call.callGemini(prompt, max_tokens = 4096)

    resp = jp.parse_json_response(response)
    if not resp:
        response = call.callGemini(prompt, max_tokens = 4096)
        resp = jp.parse_json_response(response)
    
    return resp['isJobSearch'] if 'isJobSearch' in resp else False


def search_jobs(query, isExcel = False):
    validation = _validate_query(query)
    if not validation:
        return {"error": "Invalid query", "success": False}

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_linkedin = executor.submit(linkedin.search_jobs_query, query)
        future_naukri = executor.submit(naukri.search_jobs_query, query)
        linkedin_results = future_linkedin.result()
        naukri_results = future_naukri.result()

    combined_results = linkedin_results + naukri_results
    if not combined_results:
        return {"error": "No jobs found", "success": False}

    if isExcel:
        df = pd.DataFrame(combined_results)
        df_name = _hashString(query)
        store_url = _store_to_s3(df_name, df)
        return {"success": True, "url": store_url, "data": combined_results}

    else:
        return {"success": True, "data": combined_results}


# def _parse_user_query(user_query):
#     prompt = f"""You are given with the user query from a user


def _generate_response(job_resp):
    prompt = ""
    if not job_resp:
        prompt = """
        Generarate a HTML page stating 'the query inputted is invalid and no jobs are found'.

        Give your output within <html> </html> tags. Keep background color as black.
        """
    
    else:
        url = job_resp['url']
        job_list = job_resp['data'][:5] + job_resp['data'][-4:]

        prompt = f"""
        You are given with the list of dictionaries of jobs. You have to convert it into a table in html with only three columes:
        title, Company Name and Job URL.

        Also you are given with the url to download the excel file. Write a message stating download complete file here
        and give a link to download it with hyper text 'download here'.

        Parse the following JSON list:
        {str(job_list)}

        The url is:
        {url}

        Give your output within <html> </html> tags. Keep background color as black.
        """
    
    response = call.callGemini(prompt)
    match = re.search(r"<html.*?>(.*?)</html>", response, re.DOTALL | re.IGNORECASE)
    html_content = match.group(0) if match else ""
    return html_content


def _cache(key, ip_addr, value = None, action = 'get'):

    if action == 'get':
        if not os.path.exists(f"local_cache/{ip_addr}.json"):
            return None
        
        with open(f"local_cache/{ip_addr}.json", 'r') as f:
            cache = json.load(f)
        
        return cache.get(key)
    
    elif action == 'store':
        if os.path.exists(f"local_cache/{ip_addr}.json"):
            with open(f"local_cache/{ip_addr}.json", 'r') as f:
                cache = json.load(f)
        else:
            cache = {}
        
        cache[key] = value
        with open(f"local_cache/{ip_addr}.json", 'w') as f:
            json.dump(cache, f)
        return True
    
    return False


def callAgent(user_query, ip_addr):
    key = _hashString(user_query)
    resp = _cache(key, ip_addr, action = 'get')
    if resp:
        return resp
    
    today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    hashable_str = f"{ip_addr}_{today_date_str}"

    if not _validate_query(user_query):
        error_resp = _generate_response(None)
        return error_resp
    
    job_resp = search_jobs(user_query, isExcel = True)
    html_resp = _generate_response(job_resp)

    res = _cache(key, html_resp, 'store')
    print(res)
    return html_resp



# resp = callAgent("how can we bring a bike uphill", "192.168.1.1")
# print(resp)

# resp = search_jobs("how can we bring a bike uphill")
# print(resp)