# Earnings-Calendar-Scraper-using-Selenium

## Overview

This project is a web scraping tool designed to fetch earnings calendar data from [investing.com](https://www.investing.com/earnings-calendar/). It allows users to filter earnings calendar data by country and date range, and then save the results to a CSV file for further analysis.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)

## Introduction

The Earnings Calendar Scraper is a Python script developed using Selenium and BeautifulSoup libraries. It provides a simple command-line interface for users to specify their desired filters and retrieves the earnings calendar data accordingly.
  
## Installation

To use this tool, you need to have Python 3.x installed on your system. Additionally, you'll need to install the required Python packages. You can do this using pip:

```bash
pip install selenium beautifulsoup4 pandas
```

You'll also need to have Firefox installed on your system, as the script utilizes the Firefox web browser for web scraping.

## Usage

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/harsh0701Xd/Earnings-Calendar-Scraper-using-Selenium.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Earnings-Calendar-Scraper-using-Selenium
   ```
3. Run the script:
   ```bash
   python Scrapper_script.py
   ```
4. Example:
   
   - User Input:

     ![User Input](https://github.com/harsh0701Xd/Earnings-Calendar-Scraper-using-Selenium/assets/89227170/64a979bd-7570-4db2-a662-207b03a73828)
   
   - Website display based on user input:

     ![Website Display based on user input](https://github.com/harsh0701Xd/Earnings-Calendar-Scraper-using-Selenium/assets/89227170/bb4a18ad-cb9b-4a54-84a5-3ec0c0b4a5b9)

   - Final csv output:

     ![Final Output](https://github.com/harsh0701Xd/Earnings-Calendar-Scraper-using-Selenium/assets/89227170/9e2ae4cd-4a31-4bed-bad8-9a42c277eeab)
     
