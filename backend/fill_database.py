import argparse
import asyncio
import os
import re

import aiofiles
import ijson

from db import crud, schemas
from db.database import Base, engine, get_session


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


async def parse_and_add_to_database(filename, session):
    json_file = await aiofiles.open(filename, "r")
    async for paper in ijson.items(json_file, "item"):
        remove_incomplete_attributes(paper)

        # to do: check if it is better to create a session each time a paper is created
        # (there could be some problems with multithreading
        # if we use the same session for every paper)
        crud.create_paper(schemas.Paper(**paper), session)


def fill_database(json_file):
    Base.metadata.create_all(engine)

    head, tail = os.path.split(json_file)
    prepared_json = os.path.join(head, "prepared_" + tail)
    if not os.path.exists(prepared_json):
        with open(json_file, "r", encoding="UTF-8") as input_file, open(
            prepared_json, "w", encoding="UTF-8"
        ) as output_file:
            prepare(input_file, output_file)

    with get_session() as session:
        asyncio.run(parse_and_add_to_database(prepared_json, session))

    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", default="dblpv13.json")
    args = parser.parse_args()
    print(args.filename)

    fill_database(args.filename)
