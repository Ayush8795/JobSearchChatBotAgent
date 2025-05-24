from utils import llmCaller as call
from utils import json_parser as jp
import linkedInJobs.jobFinder as jbf
import json

PAGE_NUM = 4

EXAMPLE_DICT = {
  "keyword": 'software engineer',
  "location": 'India',
  "dateSincePosted": 'past Week',
  "jobType": 'full time',
  "remoteFilter": 'remote',
  "salary": '100000',
  "experienceLevel": 'entry level',
  "limit": '10',
  "page": "0",
}

def parse_jobs_query(user_query):
    
    keys = '\n'.join(list(EXAMPLE_DICT.keys()))
    
    prompt = f"""
    You are given with a user query for job search. Parse the query and return the JSON object with the following keys:
    {keys}

    An example of the JSON object is:
     {EXAMPLE_DICT}
    
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
    filtered_jobs = []
    for job in jobs:
        filtered_jobs.append(
            {
                "title": job['position'] if 'position' in job else "",
                "companyName": job['company'] if 'company' in job else "",
                "experience": job['experience'] if 'experience' in job else "",
                "salary": job['salary'] if 'salary' in job else "",
                "location": job['location'] if 'location' in job else "",
                "jobUrl": job['jobUrl'] if 'jobUrl' in job else "",
                "description": job['description'] if 'description' in job else "",
            }
        )
    
    return filtered_jobs

def search_jobs_query(user_query):
    request_body = parse_jobs_query(user_query)
    if not request_body:
        return None
    
    for k,v in request_body.items():
        if not v:
            request_body[k] = ""
    
    all_responses = []
    for i in range(PAGE_NUM):
        pg = str(i)
        request_body["page"] = pg

        response = jbf.search_jobs(request_body)
        if response:
            all_responses += response

    filtered_jobs = _filter_jobs(all_responses)
    if not filtered_jobs:
        return None
    return filtered_jobs


# resp = search_jobs_query("sales jobs in hyderabad for freshers")
# with open("linkedInJobs.json", "w") as f:
#     json.dump(resp, f, indent=4)




