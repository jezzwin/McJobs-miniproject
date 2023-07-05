import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup


def scrape_indeed_jobs(job_title, location):
    # Create Chrome webdriver
    driver = webdriver.Chrome()
    url = "https://in.indeed.com/"
    driver.get(url)

    what_box = driver.find_element(by="xpath", value="//input[@id='text-input-what']")
    where_box = driver.find_element(by="xpath", value="//input[@id='text-input-where']")
    find_jobs_button = driver.find_element(by="xpath", value="//button[@class='yosegi-InlineWhatWhere-primaryButton']")
    what_box.send_keys(job_title)
    where_box.send_keys(location)
    find_jobs_button.click()

    df = pd.DataFrame({'Company Name': [''], 'Location': [''], 'Expected Salary': [''], 'Job Title': [''],
                       'Description About the Job': [''], 'Link': [''], 'Date Posted/Active': ['']})

    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        start = soup.find('ul', class_='jobsearch-ResultsList css-0')

        for litag in start.find_all('li'):
            try:
                title = litag.find('h2', class_='jobTitle css-1h4a4n5 eu4oa1w0').text
                company = litag.find('span', class_='companyName').text
                link = litag.find('a', class_='jcs-JobTitle css-jspxzf eu4oa1w0').get('href')
                link_full = 'https://in.indeed.com' + link
                description = litag.find('ul', {
                    'style': 'list-style-type:circle;margin-top: 0px;margin-bottom: 0px;padding-left:20px;'}).text

                try:
                    location = litag.find('div', class_='companyLocation').text
                except:
                    location = 'N/A'

                try:
                    salary = litag.find('div', class_='metadata salary-snippet-container').text
                except:
                    salary = 'N/A'

                date = litag.find('span', class_='date').text

                length = len(df)
                df.loc[length] = {'Company Name': company, 'Location': location, 'Expected Salary': salary,
                                  'Job Title': title, 'Description About the Job': description, 'Link': link_full,
                                  'Date Posted/Active': date}
            except:
                pass

        try:
            button_to_next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')
            driver.get('https://in.indeed.com' + button_to_next_page)
        except:
            print("All Data Scraped Successfully.....")
            break

    driver.quit()
    html_table = df.to_html(index=False)
    return html_table

