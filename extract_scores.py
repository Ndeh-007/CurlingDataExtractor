import os
from pathlib import Path

import workers as wk

print("constructing paths")

base_path = str(Path(__file__).parent)

country_file = os.path.join(base_path, "data", 'countries.txt')

output_folder = os.path.join(base_path, "output", "scores")

webpages_path = os.path.join(base_path, "data", "web_pages")

# load the data
HTML_FILES = wk.list_files_in_directory(webpages_path) 

# construct data grids
datagrids = wk.construct_data_grids_ii(HTML_FILES, country_file)

# save the data grids
wk.save_data_grids(output_folder, datagrids, mode="scores")

# print complete
print("Completed")