#! /usr/bin/env python3

import re
from selenium.webdriver.common.by import By 
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def open_trends_page(driver):
    driver.get('https://x.com/explore/tabs/keyword')


def open_single_trend_page(driver, url):
    driver.get(url)


def get_trends(driver):
    trends = []
    trend_urls = []
    try:
        trend_elements = driver.find_elements(By.XPATH,'//div[@data-testid="trend"]')
        
        for trend_element in trend_elements:
            try:
                trend_name = trend_element.find_element(By.XPATH, './/span[@dir="ltr"]').text
                trend_name = trend_name.replace("#","")
                trends.append(trend_name)
                trend_urls.append(f'https://x.com/search?q=%23{trend_name}&src=trend_click&vertical=trends')
            except:
                try:
                    trend_name = trend_element.find_element(By.XPATH, './/div[@class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1bymd8e"]/span').text
                    trend_name = trend_name.replace("#","")
                    trends.append(trend_name)
                    trend_urls.append(f'https://x.com/search?q=%23{trend_name}&src=trend_click&vertical=trends')
                except:
                    print("Error extracting trend name")
                    continue
        
    except Exception as e:
        print(f"Error extracting trends: {e}")
    return trends, trend_urls



def get_user_info(driver):
    page_cards = driver.find_elements(By.XPATH, '//div[@data-testid="tweet"]')
    if len(page_cards)>0:
        card=page_cards[0]
        try:
            username = card.find_element(By.XPATH, './/span').text
            userID = card.find_elements(By.XPATH, './/span[contains(text(), "@")]')[-1].text
            return username, userID
        except:
            return None,None




langs_video={"zh":"次观看","en":"views"}

def get_single_tweet(card, lang="en"):
    """Extract data from tweet card"""
    image_links = []
    video_url=""
    try:
        username = card.find_element(By.XPATH, './/span').text
    except:
        return

    try:
        #to prevent username contains @, we find all possible userid, the actual userid is the last one
        userID = card.find_elements(By.XPATH, './/span[contains(text(), "@")]')[-1].text
    except:
        return
    
    # ('Rob Nicholson', '@RobPNicholson', '2024-06-23T20:57:41.000Z', 'Rob Nicholson\n@RobPNicholson\n·\n2h#Hungary #Scotland', '', 0, 0, 0, [], '', 'https://x.com/RobPNicholson/status/1804982178691854616')

    try:
        postdate = card.find_element(By.XPATH, './/time').get_attribute('datetime')
    except:
        return

    try:
        comment = card.find_element(By.XPATH, './/div[2]/div[2]/div[1]').text
    except:
        comment = ""

    try:
        responding = card.find_element(By.XPATH, './/div[2]/div[2]/div[2]').text
    except:
        responding = ""

    text = comment + responding

    try:
        reply_cnt = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text
    except:
        reply_cnt = 0

    try:
        retweet_cnt = card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
    except:
        retweet_cnt = 0

    try:
        like_cnt = card.find_element(By.XPATH, './/div[@data-testid="like"]').text
    except:
        like_cnt = 0

    try:
        elements = card.find_elements(By.XPATH, './/div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]')
        for element in elements:
            image_links.append(element.get_attribute('src'))
    except:
        image_links = []


    try:
        promoted = card.find_element(By.XPATH, './/div[2]/div[2]/[last()]//span').text == "Promoted"
    except:
        promoted = False
    if promoted:
        return

    # get a string of all emojis contained in the tweet
    try:
        emoji_tags = card.find_elements(By.XPATH, './/img[contains(@src, "emoji")]')
    except:
        return
    emoji_list = []
    for tag in emoji_tags:
        try:
            filename = tag.get_attribute('src')
            emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
        except AttributeError:
            continue
        if emoji:
            emoji_list.append(emoji)
    emojis = ' '.join(emoji_list)

    # tweet url
    try:
        element = card.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
        tweet_url = element.get_attribute('href')
        if langs_video[lang.lower()] in text or (len(image_links)==1 and "amplify_video_thumb" in image_links[0]):
            video_url = "https://twitter.com/i/status/"+tweet_url.split("/")[-1]
            image_links=[]
    except:
        return

    tweet = (username, userID, postdate, text, emojis, reply_cnt, retweet_cnt, like_cnt, image_links,video_url, tweet_url)
    return tweet




def get_page_tweets_new(driver,data):
    page_cards = driver.find_elements(By.XPATH, '//div[@data-testid="cellInnerDiv"]')
    history_count=0
    for card in page_cards:
        tweet = get_single_tweet(card)
        if tweet:
            history_count+=1
            data.append(tweet)

        if history_count>=5:  
            break
    return history_count,driver, data