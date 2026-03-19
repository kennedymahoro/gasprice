#!/bin/bash
# Cron script to run the AAA Gas Price Scraper
cd "$(dirname "$0")"
source ../.venv/bin/activate
python scraper.py
