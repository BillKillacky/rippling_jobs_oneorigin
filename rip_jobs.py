#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import re
import os
import unicodedata

# docker considerations:
# 1. The script is designed to run in a Docker container.
# 2. The script uses the requests library to fetch web pages and BeautifulSoup to parse HTML.
# 3. The script saves job data to a JSON file in a specified directory.

# Define data directory path for persistence
DATA_DIR = '/app/data'

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Function to get the full path for a file in the data directory
def get_data_path(filename):
    return os.path.join(DATA_DIR, filename)

# Writing data to persistent storage
def save_jobs(jobs):
    with open(get_data_path('rippling_jobs.json'), 'w') as f:
        json.dump(jobs, f, indent=4)

# Reading data from persistent storage
def load_jobs():
    try:
        with open(get_data_path('rippling_jobs.json'), 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Example for saving full jobs list
def save_full_jobs(full_jobs_list):
    with open(get_data_path('rippling_jobs_full.json'), 'w') as f:
        json.dump(full_jobs_list, f, indent=4)


def main():
    process_rippling_jobs()
    get_job_description()

def get_job_description():
    print("Fetching job descriptions...\n")

    full_jobs_list = []
    work_modes = ['#LI-Onsite', '#LI-Remote', '#LI-Hybrid']
    fancy_quotes = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "—": "-",
        "–": "-",
        "…": "...",
    }

    # Load JSON data from file
    jobs_data = load_jobs()
    # with open('rippling_jobs.json', 'r') as file:
    #     jobs_data = json.load(file)

    # Loop through each job entry
    for job in jobs_data:
        job_url = job.get('job_link')

        full_jobs_dict = {}
        full_jobs_dict['job_title'] = job.get('job_title')
        full_jobs_dict['department'] = job.get('department')
        full_jobs_dict['location'] = job.get('location')
        full_jobs_dict['job_link'] = job.get('job_link')
        # "job_title": "Senior Finance Specialist",
        # "department": "Finance",
        # "location": "Scottsdale, AZ",
        # "job_link": "https://ats.rippling.com/oneorigin/jobs/8fa0ce9e-ed7a-4183-b5ce-f938196a3757"
    
        if job_url:
            try:
                response = requests.get(job_url)
                response.raise_for_status()  # Raise an error for bad responses
                soup = BeautifulSoup(response.text, 'html.parser')

                # Example: Print the page title (you can modify this to extract what you need)
                print(f"Job Title from {job_url}: \n{soup.title.string.strip() if soup.title else 'No title found'}\n")
                # Find the main job description div
                job_div = soup.find("div", class_="ATS_htmlPreview")
                if job_div:
                    full_text = job_div.get_text(separator="\n", strip=True)

                    # Remove unwanted characters
                    full_text = unicodedata.normalize("NFKD", full_text)
                    for fancy, plain in fancy_quotes.items():
                        full_text = full_text.replace(fancy, plain)

                    # Find all matching substrings
                    matches = [sub for sub in work_modes if sub in full_text]

                    work_mode = None
                    if matches:
                        print("Matched substring(s):", ", ".join(matches))
                        work_mode = matches[0].split("-")[1]
                        print(f"Work mode: {work_mode}")
                    else:
                        print("No match")
                    full_jobs_dict['work_mode'] = work_mode

                    # oneorigin_mission = full_text.split("#LI-Onsite", 1)[0]
                    if matches:
                        oneorigin_mission = full_text.split(matches[0], 1)[0]
                    else:
                        oneorigin_mission = full_text

                    oneorigin_mission = re.sub(r"OneOrigin\s*,\s*where\s*innovation\s*meets\s*imagination\s*!", 
                        "OneOrigin, where innovation meets imagination!", 
                        oneorigin_mission)

                    # job_desc = full_text.split("#LI-Onsite", 1)[1]
                    if matches:
                        job_desc = full_text.split(matches[0], 1)[1]
                    else:
                        job_desc = full_text.strip()

                    # if work_mode:
                    #     job_desc = f"Work mode: {work_mode}\n{job_desc}"

                    job_desc = job_desc[:350] + " ..." # Truncate to 350 characters
                    job_desc = job_desc.strip()        # Remove leading/trailing whitespace
                    oneorigin_mission = oneorigin_mission.strip()                         

                    full_jobs_dict['job_desc'] = job_desc
                    full_jobs_dict['oneorigin_mission'] = oneorigin_mission

                    print(f"\n--- Job Description from {job_url} ---\n")

                    full_jobs_list.append(full_jobs_dict)
                    print(f"Full Job dict:\n{json.dumps(full_jobs_dict, indent=4)}\n")
                    print("\n" + "-"*50 + "\n")

                else:
                    print(f"Could not find job description on page: {job_url}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch {job_url}: {e}")
        else:
            print("No job_link found in entry.")
    
    # write the jobs to a JSON file
    save_full_jobs(full_jobs_list)
    # with open('rippling_jobs_full.json', 'w') as f:
    #     json.dump(full_jobs_list, f, indent=4)
    
    print(f"Total jobs found: {len(full_jobs_list)}\n")


def process_rippling_jobs():

    # URL of the page to scrape
    url = "https://ats.rippling.com/oneorigin/jobs"

    # Fetch the page content
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page {url}\nStatus code: {response.status_code}")
        exit()
    

    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with class "css-oxhdrx"
    sections = soup.select('[class="css-oxhdrx"]')

    # Extract the h3 text from each section
    h3_texts = []
    for section in sections:
        h3 = section.find('h3')
        if h3:
            h3_texts.append(h3.get_text(strip=True))

    print(f"OneOrigin Open Jobs Sections: {h3_texts}\n")

    jobs = []

    # Find all top-level sections (group of jobs)
    sections = soup.select('.css-oxhdrx')

    for section in sections:
        # Optional: Get the general department name from section's <h3>
        section_heading = section.find('h3')
        section_department = section_heading.get_text(strip=True) if section_heading else None

        # Find all job blocks in this section
        job_blocks = section.select('.css-cq05mv')

        for job_block in job_blocks:
            job_link_tag = job_block.find('a', href=True)
            job_link = job_link_tag['href'] if job_link_tag else None
            job_title = job_link_tag.get_text(strip=True) if job_link_tag else None

            # Find department (from span with data-icon="DEPARTMENTS_OUTLINE")
            department = None
            dept_span = job_block.find('span', {'data-icon': 'DEPARTMENTS_OUTLINE'})
            if dept_span:
                dept_p = dept_span.find_next('p')
                if dept_p:
                    department = dept_p.get_text(strip=True)

            # Fallback to section heading if individual department not found
            if not department:
                department = section_department

            # Find location (from span with data-icon="LOCATION_OUTLINE")
            location = None
            loc_span = job_block.find('span', {'data-icon': 'LOCATION_OUTLINE'})
            if loc_span:
                loc_p = loc_span.find_next('p')
                if loc_p:
                    location = loc_p.get_text(strip=True)

            jobs.append({
                'job_title': job_title,
                'department': department,
                'location': location,
                'job_link': f"https://ats.rippling.com{job_link}"  
            })

    print(json.dumps(jobs, indent=4))

    # write the jobs to a JSON file
    save_jobs(jobs)
    # with open('rippling_jobs.json', 'w') as f:
    #     json.dump(jobs, f, indent=4)
    print(f"Total jobs found: {len(jobs)}\n")



if __name__ == '__main__':
    print("Scraping Rippling OneOrigin Open Jobs...\n")
    main()
    print("Scraping completed.")

    