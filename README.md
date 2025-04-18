# rippling_jobs_oneorigin

Webscrape the rippling OneOrigin job postings and create a json object file to read job postings into oneorigin.us website.

## Features

* Read the rippling site for OneOrigin Job postings
* using Python and BeautifulSoup4 webscraping logic to collect the job information
* Create a json file that Shashank can use to update the oneorigin.us site with fresh job postings

## Setup

* **On your local, create a data directory in your project folder (or Docker Compose will create it for you):**
* **for example: (use the your own base directory with a subfolder 'data')**
* mkdir -p /Users/billkillacky/Dev/rip_jobs_webscrape/data
* **Run your container using Docker Compose: (from your base directory)**
* cd /Users/billkillacky/Dev/rip_jobs_webscrape
* docker-compose up 
* **To run it in the background:**
* docker-compose up -d
* **To rebuild if you make changes:**
* docker-compose up --build
* docker compose up
* **With this setup, the data written in your Python script to /app/data**
* **will appear in the data subdirectory of your project folder**
* **(/Users/billkillacky/Dev/rip_jobs_webscrape/data on your local machine).**
* ~
* **confirm the tag was used**
* docker images
* docker ps


## Original Installation

* Python 3.13.1
* pip install requests
* pip install beautifulsoup4
* **(but the requirements.txt has the python modules needed)**

## Logic to consider when things break - These values can be replaced in `rip_jobs.py` when rippling changes the html code.

* **Find all top-level sections (group of jobs)**
* sections = soup.select('`.css-oxhdrx`')
* **Within each section find individual job information**
* job_blocks = section.select('`.css-cq05mv`')
* currently the OneOrigin mission statement is separated from the job description by `#LI-Onsite`. When this changes the results will vary.
* anticipated work_modes = ['`#LI-Onsite`', '`#LI-Remote`', '`#LI-Hybrid`']

## Usage

No arguments are used. Just run the rip_jobs.py code
