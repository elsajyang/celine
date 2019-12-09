import bs4
import requests
import re
from datetime import datetime, timedelta
from pytz import timezone
from dateutil.parser import parse as datetime_parse

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize web crawler values
root_url = "https://poshmark.com"
page_num = 1
get_url = lambda page_num: "https://poshmark.com/search?_=1575880000133&brand%5B%5D=Celine&category=Accessories&department=Women&max_id=" + str(page_num) + "&query=celine"
url = get_url(page_num)
max_page_num = 1

# Initialize date time values
pst = timezone('PST8PDT')
curr_time = datetime.now(pst).replace(microsecond=0)

# Initialize query terms and results
brand = "Celine"    # vs Céline
keywords = {"frame", "frames", "glasses", "sunglass", "sunglasses", "shade", "shades"}
new_posts = []

# Iterate through first few pages
while (page_num <= max_page_num):
    # Download a page
    get_page = requests.get(url)
    get_page.raise_for_status()
    print("Searching {}".format{page_num})


    # Parse text for items
    page = bs4.BeautifulSoup(get_page.text, 'html.parser')
    posts = page.find_all('div', {'class': 'tile', 'data-post-brand': brand})

    for p in posts:
        date_posted = p.get('data-created-at')
        brand_posted = p.get('data-post-brand')
        add_info = p.find('a', {'class': 'covershot-con'})
        title_posted = add_info.get('title')
        listing_url = add_info.get('href')

        # Do some data cleaning
        date_posted = datetime_parse(date_posted)
        brand_posted = brand_posted.lower()
        title_posted = title_posted.lower()
        listing_url = listing_url.lower()

        if re.search("celine", brand_posted) is not None:
            for kw in keywords:
                title_contains = re.search(kw, title_posted)
                url_contains = re.search(kw, listing_url)
                if title_contains is not None or url_contains is not None:
                    if curr_time - timedelta(days=1) < date_posted < curr_time:
                        new_posts.append((title_posted, root_url + listing_url))
                        break;

    page_num += 1
    url = get_url(page_num)

if new_posts:
    # Compose the email 
    mail = MIMEMultipart()
    mail['Subject'] = 'celine alert'
    msg = """
    <p> Newest celine sunglasses listings
    <br>
    """
    for p in new_posts:
        msg += "<a href=" + p[1] + ">" + p[0] + "<br>"
    mail.attach(MIMEText(msg, 'html'))
    print(msg)
    # try:
    user = 'elsajy@gmail.com'
    password = 'mazwobpzctryiztt'
    to_addr = 'elsajy@gmail.com'

    # Send the e-mail alert
    conn = smtplib.SMTP_SSL('smtp.gmail.com', 465) # smtp address and port
    # conn.starttls() # starts tls encryption. When we send our password it will be encrypted.
    conn.login(user, password)
    conn.sendmail(user, to_addr, mail.as_string())
    conn.quit()
    print('Sent notification e-mails to the following recipients:\n')
    print(user)
    print('')
    # except:
    #     print('Something went wrong...')
else:
    # Print to console if no new posts
    print("No new posts for today")
