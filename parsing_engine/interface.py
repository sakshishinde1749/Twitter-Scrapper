#! /usr/bin/env python3

import csv
import os
from time import sleep

from parsing_engine.driver import *
from parsing_engine.login.login_twitter import *
from parsing_engine.log import get_logger
from .engine import open_trends_page,get_trends, open_single_trend_page, get_page_tweets_new




def check_dir(dir):
    '''
    check the dir is exist or not. if it does not exist, create the dir
    '''
    if not os.path.exists(dir):
        os.makedirs(dir)
        return False
    else:
        return True




def scrap_trends(save_dir, headless=False):
    logger = get_logger()
    driver = init_driver(headless, show_images=False)
    try:
        login_cookie(driver)
        sleep(10)
        open_trends_page(driver)
        sleep(10)
        trends, trend_urls = get_trends(driver)
        for trend_url in trend_urls:
            open_single_trend_page(driver, trend_url)
            sleep(10)
            data = []
            get_page_tweets_new(driver, data)
           
        if trends:
            check_dir(save_dir)
            csv_logfile_name = os.path.join(save_dir, "trends.csv")
            with open(csv_logfile_name, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                header = ["Trend"] + ["Tweet " + str(i) for i in range(1, 6)]
                writer.writerow(header)
                
                # Write the trends and tweets
                for trend_index, trend in enumerate(trends):
                    row = [trend]  # Start with the trend
                    # Add the tweets for the current trend
                    try:
                        row.extend(data[trend_index])
                    except IndexError:
                        pass
                    writer.writerow(row)
                       
            logger.info("Trends scraped successfully.")
        else:
            logger.warning("No trends found.")
    except Exception as e:
        logger.exception(f"An error occurred while scraping trends: {e}")
    finally:
        driver.quit()