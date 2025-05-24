from utils import llmCaller as call
from utils import json_parser as jp
import naukriJobs.jobFinder as jbf
import json


base_url = "https://www.naukri.com/"
PAGE_NUM = 4

def parse_search_query(user_query):
    prompt = f"""
    You are given with the user query for a job search. Parse the query and find the following keys:
    search - the user search
    location - the job location
    experience - the experience level for job (if given a range then give lower bound and if following are given then give corresponding value:
    freshers - 0
    entry level - 1
    mid level - 2
    senior level - 3
    director level - 4
    any other or not given - 0)
    salary - the expected salary

    Give the output in following JSON format:
    {{
        "search": "<search>",
        "location": "<location>",
        "experience": <experience>,
        "salary": <salary>
    }}

    Example:
    for user query: "software engineer jobs in bangalore for freshers"
    
    output in JSON is:
    {{
        "search": "software engineer",
        "location": "bangalore",
        "experience": 0,
        "salary": null
    }}

    Example:
    for user query: "software engineer jobs in bangalore for 2 years experience"
    output in JSON is:
    {{
        "search": "software engineer",
        "location": "bangalore",
        "experience": 2,
        "salary": null
    }}

    Now parse the following user query:
    {user_query}
    """

    response = call.callGemini(prompt, max_tokens = 4096)
    resp = jp.parse_json_response(response)

    if not resp:
        response = call.callGemini(prompt, max_tokens = 4096)    
        resp = jp.parse_json_response(response)
    
    return resp

def _filter_jobs(jobs):
    checkList = set()
    filtered_jobs = []

    for job in jobs:

        if job['jobId'] not in checkList and 'jdURL' in job and 'title' in job and 'companyName' in job:
            jdurl = job['jdURL'][1:] if job['jdURL'].startswith("/") else job['jdURL']
            filtered_jobs.append({
                "title": job['title'],
                "companyName": job['companyName'],
                "experience": job['placeholders'][0]['label'] if 'placeholders' in job and len(job['placeholders']) > 0 else "",
                "salary": job['placeholders'][1]['label'] if 'placeholders' in job and len(job['placeholders']) > 1 else "",
                "location": job['placeholders'][2]['label'] if 'placeholders' in job and len(job['placeholders']) > 2 else "",
                "jobUrl": base_url + jdurl,
                "description": job['jobDescription'] if 'jobDescription' in job else "",
            })
            checkList.add(job['jobId'])
    
    return filtered_jobs


def search_jobs_query(user_query):
    parsed_query = parse_search_query(user_query)
    if not parsed_query:
        return None
    
    seoKey = '-'.join(parsed_query['search'].split())
    if parsed_query['location']:
        seoKey += '-jobs-in-' + '-'.join(parsed_query['location'].split())
    if parsed_query['experience']:
        seoKey += '-experience-' + str(parsed_query['experience'])
    if parsed_query['salary']:
        seoKey += '-salary-' + str(parsed_query['salary'])

    all_responses = []
    for i in range(1, PAGE_NUM):
        if i > 1:
            seoKey += '-' + str(i)
        
        search_url = base_url + seoKey
        print("search url: =====>", search_url)
        print("\n="*2)
        jobs = jbf.search_jobs(search_url)
        print(jobs['jobs'][0]['title'])
        print("\n="*2)
        all_responses += jobs['jobs']
        seoKey = jobs['url']

    final_resp = _filter_jobs(all_responses)
    return final_resp


# all_resp = search_jobs_query("sales jobs for freshers in hyderabad")
# with open("naukriJobs2.json", "w") as f:
#     json.dump(all_resp, f, indent=4)

