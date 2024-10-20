import pandas as pd
import numpy as np
import warnings
import os

from bs4 import BeautifulSoup

import logging
logging.basicConfig(filename='app.log', filemode='w', level=logging.WARNING)

def list_files_in_directory(directory_path):
    # Get the list of all files and directories in the specified directory
    files = os.listdir(directory_path)

    # Filter out directories, keeping only files
    files = [
        os.path.join(directory_path, file)
        for file in files
        if os.path.isfile(os.path.join(directory_path, file))
    ]

    return files


def create_dictionaries_from_file(file_path):
    country_to_abbr = {}
    abbr_to_country = {}

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Assuming the format is 'Country - Abbreviation'
            country, abbr = line.strip().split(" - ")
            country_to_abbr[country] = abbr
            abbr_to_country[abbr] = country

    return country_to_abbr, abbr_to_country



class DataGrid:
    def __init__(self, name: str) -> None:

        self.countries = []
        self.draws = []
        self.grid: None | np.ndarray = None
        self.name = name
        self.drawScores: list[dict[str, str|np.ndarray]] = []
        # {draw_name:str, country_one:str, country_two:str, scoreboard: np.ndarray((2,10), dtype=object)}

    def prime(self, opts: dict[str, list[str]], store: dict[str, str]):
        """Initializes the contents of the datagrid, preparing it to recieve data

        Args:
            opts (dict[str, list[str]]): data to configure the data grid with
            store (dict[str, str]): the name store used to get abbreviations of names
        """
        countries_abv = []

        country_full_names = opts["countries"]
        draws = opts["draws"]

        for name in country_full_names:
            try:
                abv = store.get(name)
                if abv is None:
                    warnings.warn(
                        f"abreviation not found for country <{name}>, scores will not be registered"
                    )
                else:
                    countries_abv.append(store[name])
            except Warning as w:
                logging.warning("Warning Occurred", exc_info=True)

        data = (
            np.ones(
                (len(countries_abv), len(countries_abv), len(draws)), dtype=object
            )
            * -1
        )
        self.countries = countries_abv
        self.draws = draws
        self.grid = data

    def addEntry(self, country_one: str, country_two: str, draw: str, value: str):
        """
        Contries are abreviation

        Args:
            country_one (str): a country that participated
            country_two (str): a correspoding country in that draw
            draw (str): the draw in which the particpation took place
            value (str): the value of the face between both counties. corresponding to country_one
        """

        x = self.countries.index(country_one)
        y = self.countries.index(country_two)
        z = self.draws.index(draw)

        self.grid[x, y, z] = value

    def addDrawEntry(self, scores: list[dict[str, str | np.ndarray]], draw: str, tournament: str):
        opts = {
            "draw": draw,
            "scores": scores ,
            "tournament": tournament,
        }
        self.drawScores.append(opts)

    def exportDrawScores(self, folder: str):
        for score_box in self.drawScores:
            parent = os.path.join(folder, score_box['tournament'])
            os.makedirs(parent, exist_ok=True)

            for box in score_box['scores']:
                # create the draws folder
                parent = os.path.join(parent, score_box['draw'])
                os.makedirs(parent, exist_ok=True)

                c1 = box['country_one']
                c2 = box['country_two']
                score: np.ndarray = box['value']
                game_time = box['game_time']

                file_name = f"{c1}_{c2}.csv"
                path = os.path.join(parent, file_name)
                df = pd.DataFrame(score, 
                                columns=list(range(score.shape[1])),
                                index=[c1, c2]
                                )
                df.to_csv(path)

    def export(self, folder: str, file_name: str = None):
        """
        Writes data to file_name.csv file
        """
        _name = self.name if file_name is None else file_name

        # for all draws
        # so we have tournament_name/draw_x
        for k in range(self.grid.shape[-1]):
            parent = os.path.join(folder, _name)
            os.makedirs(parent, exist_ok=True)

            path = os.path.join(parent, f"draw_{self.draws[k]}.csv")
            df = pd.DataFrame(
                self.grid[:, :, k], columns=self.countries, index=self.countries
            )
            df.to_csv(path)


def get_html_content(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    return BeautifulSoup(html_content, "lxml")


def extract_meta_data(
    soup: BeautifulSoup, store: dict[str, str]
) -> tuple[str, list[str], list[str]]:
    """gets data for each tournament

    Args:
        soup (BeautifulSoup): Parsed HTML file
        store (dict[str, str]): short_name -> long_name

    Returns:
        tuple[str, list[str], list[str]]: name, list of countries (Full names), list of draws
    """
    name = ""
    countries = []
    draws = []

    # NAME IS  the tornament name in lowercase aand underscores to repalce the spaces
    # countries a list of countires taking part in the tournament
    # a list of draws in the tournament

    # extract the list of countries
    info_teams_tab = soup.find("div", id="infoteams")
    team_sections = info_teams_tab.find_all("div", class_="col-md-6")
    for team in team_sections:
        country_name = team.find("h5")
        countries.append(country_name.get_text(strip=True))

    # extract the draws
    info_results = soup.find("div", id="inforesults")
    p_tag = info_results.find("div", class_="col-md-12").find("p")
    anchor_tags = p_tag.findAll("a")

    for tag in anchor_tags:
        value = tag.get_text(strip=True)
        if value not in store.keys():
            draws.append(value)

    # extract the name of the tournament
    body = soup.find("body")
    h2 = body.findAll("h2")[0]
    _name: str = h2.get_text(strip=True)
    name = _name.lower().replace(" ", "_")

    return name, countries, draws


def extract_draw_information(soup: BeautifulSoup) -> list[dict[str, str]]:
    """gets the draw information for all available draws
        each data will be reversed to match the read oders
        say we have

        teams: C1 , C2
        draw: D
        scores: S1, S2

        ttwo data instances will be extracted from here
        1. C1, C2, D, S1
        2. C2, C1, D, S2


    Args:
        soup (BeautifulSoup): the data to be parsed

    Returns:
        list[dict[str, str]]: results of the parsing. a list of dictionaries carrying
        the two counties that took part in the draw, the draw and  the value of an instance of participation
    """
    data = []

    info_draw = soup.find("div", id="infodraw")
    tables = info_draw.findAll("table", class_="table")
    for table in tables:
        # tbody = table.find("tbody")
        # if tbody is None:
        #     continue

        tds = table.findAll("td", class_="col-md-2")
        for td in tds:
            td_content = td.get_text(separator="\n").strip()
            content_array = td_content.split("\n")
            if len(content_array) == 1:
                continue
            d = content_array[0].strip()[1:-1]
            c1, c2 = content_array[2].strip().split(" - ")
            s1, s2 = content_array[4].strip().split(" - ")

            opts_1 = {"country_one": c1, "country_two": c2, "draw": d, "value": s1}
            opts_2 = {"country_one": c2, "country_two": c1, "draw": d, "value": s2}

            data.append(opts_1)
            data.append(opts_2)

    return data

def extract_draw_information_ii(soup: BeautifulSoup, store: dict[str, str]) -> list[dict[str, object]]:
    data = []
    info_results_display = soup.find("div", id="resultdisplay")
    ird_sections: list[BeautifulSoup] = info_results_display.find("div", class_='col-md-12').findAll("div", class_='col-md-12')

    for section in ird_sections:
        sec_opts = {}

        sec_opts['scores'] = []

        tables: list[BeautifulSoup] = section.findAll("table", class_="game-table")
        
        for table in tables:
            score_otps = {}
            score_otps["game_time"] = ""

            thead = table.find("thead")
            draw_name = thead.find("th", class_="game-header").get_text(strip=True)
            sec_opts["draw"] = draw_name.lower().replace(" ", "_")

            tbody = table.find("tbody")
            trs: list[BeautifulSoup] = tbody.find_all("tr")

            c1 = trs[0].find("td", class_="game-team").get_text(strip="True")
            c2 = trs[1].find("td", class_="game-team").get_text(strip="True")

            tds_0 = trs[0].findAll("td", class_="game-end10")
            tds_1 = trs[1].findAll("td", class_="game-end10")

            arr = np.array([
                [tds_i.get_text(strip="True") for tds_i in tds_0] + [trs[0].findAll("td", class_="game-total")[0].get_text(strip="True")],
                [tds_i.get_text(strip="True") for tds_i in tds_1] + [trs[1].findAll("td", class_="game-total")[0].get_text(strip="True")],
            ], dtype=object)

            score_otps["value"] = arr
            score_otps["country_one"] = store[c1]
            score_otps['country_two'] = store[c2]

            # append to sec_opts
            sec_opts['scores'].append(score_otps)

        # collect the section data
        data.append(sec_opts)

    return data


def construct_data_grids_ii(html_files: list[str], country_file: str) -> list[DataGrid]:

    print("constructing data grids")

    FULL_TO_ABBV, ABBV_TO_FULL = create_dictionaries_from_file(country_file)

    datagrids: list[DataGrid] = []

    for file in html_files:

        try: # load the file into system
            soup = get_html_content(file)

            # get the basic meta data
            name, countries, draws = extract_meta_data(soup, ABBV_TO_FULL)
            # print(draws)

            # get the name of the file
            grid = DataGrid(name)

            # prime the data grid
            opts = {"countries": countries, "draws": draws}
            grid.prime(opts, FULL_TO_ABBV)

            # obtain the draw data
            draw_data: list[dict[str, object]] = extract_draw_information_ii(soup, FULL_TO_ABBV)

            # for each entry in the draw data, update the datagrid
            for data in draw_data:
                grid.addDrawEntry(
                    data.get("scores"), data.get("draw"), name
                )

            # collect the populated grid
            datagrids.append(grid)

            print(f"Grid: {grid.name}")
        except Warning as w:
            logging.warning("Warning occurred", exc_info=True)
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    return datagrids


def construct_data_grids(html_files: list[str], country_file: str) -> list[DataGrid]:
    """constructs and resolves the data grids from the provided list of html files

    Args:
        html_files (str): list of html files
        country_file (str): the file which hold full_country -> abbv country names

    Returns:
        list[DataGrid]: the parsed data for each file
    """

    print("constructing data grids")

    FULL_TO_ABBV, ABBV_TO_FULL = create_dictionaries_from_file(country_file)

    datagrids: list[DataGrid] = []

    for file in html_files:

        try: # load the file into system
            soup = get_html_content(file)

            # get the basic meta data
            name, countries, draws = extract_meta_data(soup, ABBV_TO_FULL)
            # print(draws)

            # get the name of the file
            grid = DataGrid(name)

            # prime the data grid
            opts = {"countries": countries, "draws": draws}
            grid.prime(opts, FULL_TO_ABBV)

            # obtain the draw data
            draw_data: list[dict[str, str]] = extract_draw_information(soup)

            # for each entry in the draw data, update the datagrid
            for data in draw_data:
                grid.addEntry(
                    data["country_one"], data["country_two"], data["draw"], data["value"]
                )

            # collect the populated grid
            datagrids.append(grid)

            print(f"Grid: {grid.name}")
        except Warning as w:
            logging.warning("Warning occurred", exc_info=True)
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)

    return datagrids


def save_data_grids(folder: str, datagrids: list[DataGrid], mode="normal"):
    """calls export propertey on all datagrids

    Args:
        folder (str): the base folder where the data will be stored
        datagrids (list[DataGrid]): the data grids to be stored
    """
    print("saving datagrids")
    for grid in datagrids:
        print(f"saving grid: {grid.name}")
        if mode=="normal":
            grid.export(folder, grid.name)
        if mode =="scores":
            grid.exportDrawScores(folder)


