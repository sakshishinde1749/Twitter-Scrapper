#! /usr/bin/env python3

import argparse

from parsing_engine import interface
from parsing_engine.login.login_twitter import login_pwd

parser = argparse.ArgumentParser(description='T-Scraper: A Twitter scraper that overrides some limits of official Twitter API')
parser.add_argument("-t", "--trends", action="store_true", help="Scrape trends from Twitter")
args = parser.parse_args()



if args.trends:
    interface.scrap_trends(args.savedir, headless=not args.pop)
