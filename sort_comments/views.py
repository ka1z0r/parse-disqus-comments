from django.shortcuts import render
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Create your views here.
def index(request):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://the-flow.ru/releases/oxxxymiron-krasota-i-urodstvo")

    wait = WebDriverWait(driver, 300)
    wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='Disqus']")))

    while True:
        try:
            element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "load-more__button")))
            element.click()
        except:
            break

    c = driver.page_source
    driver.quit()

    soup = BeautifulSoup(c, 'html.parser')
    comments = soup.find_all("div", {"class": "post-content"})

    all_comments = []
    for article in comments:
        comment = {}
        # try/except для отлова удаленных комментариев
        try:
            comment["username"] = article.find("span", {"class": "author publisher-anchor-color"}).get_text()
            comment["user_url"] = article.find("span", {"class": "author publisher-anchor-color"}).a['href']
            comment["time"] = ",".join(article.find("a", {"class": "time-ago"}).get("title").split(",")[1:])
            comment["raw_comment"] = str(article.find("div", {"data-role": "message"})).split('<a class="media-button')[0]
            # comment["raw_comment"] = str(article.find("div", {"class": "post-message"}))
            content = article.find("div", {"data-role": "message"}).find("a", {"class": "media-button-expand"})
            if content:
                comment["content_url"] = content.get("href")
            else:
                comment["content_url"] = None
            comment["comment_url"] = article.find("a", {"class": "time-ago"}).get("href")
            comment["score"] = int(article.find("span", {"data-role": "likes"}).get_text())
            all_comments.append(comment)
        except:
            pass

    all_comments.sort(key=lambda d: d['score'], reverse=True)
    print(len(all_comments))

    return render(request, "sort_comments/index.html", {'comments': all_comments})
