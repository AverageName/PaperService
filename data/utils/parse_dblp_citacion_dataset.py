import numpy as np # linear algebra
import pandas as pd

! pip install ijson

import ijson
import time
from tqdm import tqdm
import pprint
pp = pprint.PrettyPrinter(width=180).pprint
import gc

def get_all_colnames(n=10000):
    all_colnames = ['id', 'title', 'authors', 'venue', 'year', 'fos',
                    'references', 'n_citation', 'page_start', 'page_end',
                    'doc_type', 'publisher', 'volume', 'issue', 'doi', 'indexed_abstract']
#     with open('../input/citation-network-dataset/dblp.v12.json', "rb") as f:
#         for i, element in enumerate(tqdm(ijson.items(f, "item"))):
#             all_colnames |= set(element.keys())
#             if i == n:
#                 break
    return all_colnames

def get_datalist(n=300_000, colnames=None):
    colnames = colnames if colnames else get_all_colnames()
    datalist = list()
    with open('../input/citation-network-dataset/dblp.v12.json', "rb") as f:
        for i, element in enumerate(tqdm(ijson.items(f, "item"))):
            paper = {colname: element.get(colname, np.nan) for colname in colnames}
            datalist.append(paper)
            if i == n:
                break
    return datalist

datalist = get_datalist()
df = pd.DataFrame(datalist)

del datalist
gc.collect()
