# CURLING DATA EXTRACTOR

Project contains code for manual extraction of data from https://results.worldcurling.org/Championship/Type/1

This is by no means an optimal solution. Thankfully the data base is small the and webpages can be downloaded manually

The ideal solution will be build a crawler to load the pages and perform the extraction. This has a higher learning curve than the required alotted time frame, hence the manual approach

But there is beauty in manual labour, why automate, when you can suffer

Please Read through to the end

## Usage


### Prerequisites

1. Make sure python is installed, see here for installation guide https://www.python.org/downloads/

2. Making data available for extraction. This will be tedious🥲. Repeat this process for as many pages as needed


    1. Visit the target page, e.g https://results.worldcurling.org/Championship/Details/763

    2. Navigate to the `Results` Tab
        ![alt text](/images/image1.png)
    3. Click `show all games`, and wait for the data to load
    4. Save the page to `data/webpages/`. see Windows OS guide below. for MacOS it should be similar, the browser in use is Chrome
        
        0. ![alt text](/images/image2.png)
        1. Press `Ctrl + S`
        2. Ensure the save type is `webpage, complete`
        3. Use a name of your choice. (best to just copy the title of the tournament for the webpage and here. It will help when navigating the directories)

3. Once data is made available, the extraction process can begin.

### Getting Started

1. Clone this repository to a chosen folder
2. Using the terminal, navigate to that folder
3. Create and activate virtual environment in that folder

    1. creating virtual environment
        ```commadLine
        python -m venv venv
        ```
    2. Activating virtaul environment
        ```commandLine
        venv/Scripts/activate
        ```
4. Run the script of your choice to extract data from the html files that have been initially downloaded. For example to extract score boxes 
    ```commandLine
    python extract_scores.py
    ```
5. Check the `app.log` file for errors after a run. If there were errors during the parsing of a particular file, the extractor will skip that file and progress to the next.

    1. countries.txt contains key value pairs of country names and their abbreviations
    2. if in the log file there is something relating to an abbreviation not existing, update the countries file accordingly and re-run the target script

6. All extracted data is sent to the target outputs. `extract_scores.py -> output\scores` and `extract_totals -> output\total_scores`

7. See Examples in `./ouptut` and `./data`. \
8. Note: *__Running New Extraction Will Overrided Existing Data.__*


### Intepreting Data

---

#### output\total_scores\
Contains folders of tournaments(each downloaded webpage). Each of these folders(tournaments) contains draw total results

the results are in a `(N,N)` grid, where `N` is the number of countries participating in that tournament.
- The score at each cell is the results of country_i vs country_j. 
- cells with values of -1 are invalid, meaning they did not participate in the current draw.
- the name of each file is the current draw

These results do not show the score box values per draw.

---

#### output\scores\
This folder contains a list of folders which are the tournaments(gotten from the downloaded webfiles)

Each folder has sub folder of draws.
Each draw folder contains the scoreboxes for each game played in that draw.

The totals should be the last column of each grid.