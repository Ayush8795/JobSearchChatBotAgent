import requests
from bs4 import BeautifulSoup
import re
import logging

url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.linkedin.com/jobs",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}


def parse_job_list(job_data):
    """
    Parse job listings from HTML data using BeautifulSoup.
    
    Args:
        job_data (str): HTML string containing job listings
        
    Returns:
        list: List of dictionaries containing job information
    """
    try:
        soup = BeautifulSoup(job_data, 'html.parser')
        jobs = soup.find_all("li")
        parsed_jobs = []
        
        for index, job_element in enumerate(jobs):
            try:
                # Extract position
                position_elem = job_element.find(class_="base-search-card__title")
                position = position_elem.get_text(strip=True) if position_elem else ""
                
                # Extract company
                company_elem = job_element.find(class_="base-search-card__subtitle")
                company = company_elem.get_text(strip=True) if company_elem else ""
                
                # Extract location
                location_elem = job_element.find(class_="job-search-card__location")
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                # Extract date
                date_elem = job_element.find("time")
                date = date_elem.get("datetime") if date_elem else ""
                
                # Extract salary
                salary_elem = job_element.find(class_="job-search-card__salary-info")
                if salary_elem:
                    salary_text = salary_elem.get_text(strip=True)
                    # Replace multiple whitespaces with single space
                    salary = re.sub(r'\s+', ' ', salary_text)
                else:
                    salary = ""
                
                # Extract job URL
                job_url_elem = job_element.find(class_="base-card__full-link")
                job_url = job_url_elem.get("href") if job_url_elem else ""
                
                # Extract company logo
                logo_elem = job_element.find(class_="artdeco-entity-image")
                company_logo = logo_elem.get("data-delayed-url") if logo_elem else ""
                
                # Extract ago time
                ago_time_elem = job_element.find(class_="job-search-card__listdate")
                ago_time = ago_time_elem.get_text(strip=True) if ago_time_elem else ""
                
                # Only return job if we have at least position and company
                if not position or not company:
                    continue
                
                job_dict = {
                    "position": position,
                    "company": company,
                    "location": location,
                    "date": date,
                    "salary": salary if salary else "Not specified",
                    "jobUrl": job_url,
                    "companyLogo": company_logo,
                    "agoTime": ago_time
                }
                
                parsed_jobs.append(job_dict)
                
            except Exception as err:
                logging.warning(f"Error parsing job at index {index}: {str(err)}")
                continue
        
        return parsed_jobs
        
    except Exception as error:
        logging.error(f"Error parsing job list: {str(error)}")
        return []


def search_jobs(request_body):
    response = requests.get(url, headers = headers, params = request_body)
    parsed_resp = parse_job_list(response.text)
    # print(parsed_resp)
    return parsed_resp




