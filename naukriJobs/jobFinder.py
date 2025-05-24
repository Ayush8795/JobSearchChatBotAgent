from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests

base_url = "https://www.naukri.com/"

def _parse_seoKey(seoKey):
    wdLis = seoKey.split("-")
    if len(wdLis) == 0:
        return ""
    
    return '-'.join([x for x in wdLis if not x.isdigit()])

def _get_response(request):
    try:
        headers_list = str(request.headers).split("\n")
        headers = {}
        for header in headers_list:
            try:
                k,v = header.split(": ")
            except:
                continue
            headers[k] = v
        
        if str(request.url).startswith("https://www.naukri.com/jobapi/v3/search"):
            response = requests.get(request.url, headers = headers)
            json_resp = response.json()
            
            if not json_resp:
                return None
            if 'jobDetails' not in json_resp:
                return None
            
            return json_resp
        else:
            print("skipping request: ", request.url)
            return None
    except Exception as e:
        print("Error: ", e)
        return None


def search_jobs(search_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    
    print(search_url)
    driver.get(search_url)
    print("sleep for 3 sec")
    time.sleep(3)

    found_resp = {
        "url": "",
        "jobs": []
    }
    for request in driver.requests:
        if request.response:
            job_response = _get_response(request)
            if not job_response:
                continue

            found_resp['url'] = _parse_seoKey(job_response['queryParamMap']['seoKey'])
            found_resp['jobs'] = job_response['jobDetails']
            print("=="*30)
            print(found_resp['url'])
            print(job_response['jobDetails'][0]['title'])
            print("=="*30)
            break
    
    return found_resp


# listt = search_jobs("https://www.naukri.com/sales-jobs-in-hyderabad-secunderabad-3")
# print(listt)
# with open("testnaukri.json", "w") as f:
#     json.dump(listt, f, indent = 4)