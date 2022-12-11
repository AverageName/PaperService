import argparse
import asyncio
import os
import sys
import re
import pandas as pd
from tqdm import tqdm
import ast

import aiofiles
import ijson

from db import crud, schemas
from db.database import Base, engine, get_session


COLNAMES = ["id", "title", "authors", "venue", "year", "keywords", "fos",
            "references", "n_citation", "page_start", "page_end", "lang",
            "volume", "issue", "issn", "isbn", "doi", "pdf", "url", "abstract"]

CONTAINER_COLNAMES = ["venue", "authors", "keywords", "fos", "references", "url"]


def prepare(input_file, output_file):
    for line in input_file:
        line = re.sub(r"\"_id\"", '"id"', line)
        line = re.sub(r"\"name_d\"", '"name"', line)
        line = re.sub(r"NumberInt\(([0-9]+)\)", r"\1", line)
        output_file.write(line)


def remove_incomplete_attributes(paper: dict):
    venue = paper.get("venue")
    # beware of the empty dict case!
    # (it won't pass "if venue" check, but should be processed)
    if venue is not None:
        if "id" not in venue:
            del paper["venue"]

    authors = paper.get("authors")
    if authors:
        authors[:] = [author for author in authors if "id" in author]


async def parse_json_and_add_to_database(filename, session):
    json_file = await aiofiles.open(filename, "r")
    counter = 0
    async for paper in ijson.items(json_file, "item"):
        remove_incomplete_attributes(paper)

        # to do: check if it is better to create a session each time a paper is created
        # (there could be some problems with multithreading
        # if we use the same session for every paper)
        crud.create_paper(schemas.Paper(**paper), session)
        counter += 1
        print(counter)
        if counter == 100:
            break


def fill_database_with_json(json_file):
    if not os.path.isfile(json_file):
        print("ERROR: JSON file path wrong, file does not exists!", file=sys.stderr)
    else:
        print("Yeah boy fisting time cumming", file=sys.stderr)

    Base.metadata.create_all(engine)

    head, tail = os.path.split(json_file)
    prepared_json = os.path.join(head, "prepared_" + tail)
    if not os.path.exists(prepared_json):
        with open(json_file, "r", encoding="UTF-8") as input_file, open(
            prepared_json, "w", encoding="UTF-8"
        ) as output_file:
            prepare(input_file, output_file)

    with get_session() as session:
        asyncio.run(parse_json_and_add_to_database(prepared_json, session))

    engine.dispose()


def parse_csv_and_add_to_database(filename, session):
    df = pd.read_csv(filename)
    for counter, paper in tqdm(enumerate(df.iterrows())):
        if counter == 100:
            break
        paper = dict(paper[1])
        #paper = {k: ast.literal_eval(v) if k in CONTAINER_COLUMNSS else v for k, v in paper.items()}
        for k, v in paper.items():
            try:
                paper[k] = ast.literal_eval(v)
            except (SyntaxError, ValueError):
                continue
            finally:
                if k in CONTAINER_COLNAMES and not isinstance(paper[k], (list, dict, tuple)):
                    paper[k] = list()
        remove_incomplete_attributes(paper)
        crud.create_paper(schemas.Paper(**paper), session)


def fill_database_with_csv(csv_file):
    Base.metadata.create_all(engine)
    with get_session() as session:
        parse_csv_and_add_to_database(csv_file, session)
    engine.dispose()


def fill_database(file):
    print(file, file=sys.stderr)
    print(os.path.splitext(file), file=sys.stderr)
    if os.path.splitext(file)[-1] == ".csv":
        fill_database_with_csv(file)
    else:
        fill_database_with_json(file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default="dblpv13.json")
    args = parser.parse_args()
    print(args.filename)

    fill_database(args.filename)
