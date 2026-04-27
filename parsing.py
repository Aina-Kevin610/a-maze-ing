import os
from typing import Any


class ParseError(Exception):
    def __init__(self, msg: str = "Invalid config format!") -> None:
        self.msg = msg


def read_file(filename: str) -> list[str]:
    content: list[str] = []
    f = None
    try:
        if filename != "config.txt":
            raise ParseError("Invalid filename!")
        f = open(filename, "r")
        content = f.read().strip().splitlines()
    except ParseError as e:
        print("Error - ", e)
    except FileNotFoundError:
        print("Error - File not found!")
    finally:
        if f is not None:
            f.close()
    return content


def remove_space(content: list[str]) -> list[str]:
    return [x for x in content if x != '']


def comment_at_first(content: list[str]) -> list[str]:
    return [x for x in content if x[0] != '#']


def comment_at_end(content: list[str]) -> list[list[str]]:
    stripped = [x.strip() for x in content]
    split = [x.split("#") for x in stripped]
    for x in split:
        lgh = len(x)
        if lgh >= 2:
            i = 1
            while i < lgh:
                del x[1]
                i += 1
    return split


def clean_str(content: list[list[str]]) -> list[str]:
    result = [str(set(x)) for x in content]
    result = [x.replace("{", "") for x in result]
    result = [x.replace("}", "") for x in result]
    result = [x.replace("'", "") for x in result]
    return result


def test_len_error(content: list[str]) -> list[tuple[str, ...]]:
    tuples: list[tuple[str, ...]] = [
        tuple(x.replace(" ", "").split("=")) for x in content
    ]
    try:
        for x in tuples:
            if len(x) != 2:
                raise ParseError("Invalid config format!")
        return tuples
    except ParseError as e:
        print("Error - ", e)
        os._exit(0)


def convert_to_dict(content: list[tuple[str, ...]]) -> dict[str, str]:
    return {x[0]: x[1].strip() for x in content}


def entry_exit(new_content: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = dict(new_content)
    result["ENTRY"] = tuple(new_content["ENTRY"].split(","))
    result["EXIT"] = tuple(new_content["EXIT"].split(","))
    return result


def is_valid(final: dict[str, Any]) -> None:
    try:
        str(final["ALGO"])
        int(final["ENTRY"][0])
        int(final["ENTRY"][1])
        int(final["EXIT"][0])
        int(final["EXIT"][1])
        str(final["PERFECT"])
        if int(final["WIDTH"]) <= 7 or int(final["HEIGHT"]) <= 5:
            raise ParseError("Too small HEIGHT or WIDTH!")
        if not final["OUTPUT_FILE"].endswith(".txt"):
            raise ParseError("FILE OUTPUT's extension must be '.txt' !")
        if final["PERFECT"] != "True" and final["PERFECT"] != "False":
            raise ParseError("PERFECT option must be boolean!")
        if final["ALGO"] != "DFS":
            raise ParseError("Unknown parameter for ALGO!")
        if len(final["ENTRY"]) != 2 or len(final["EXIT"]) != 2:
            raise ParseError("Invalid ENTRY or EXIT parameter!")
    except Exception as e:
        print("Error - ", e)
        os._exit(0)


def parse_config(filename: str = "config.txt") -> dict[str, Any]:
    content = read_file(filename)
    no_space = remove_space(content)
    no_cmt1 = comment_at_first(no_space)
    no_cmt2 = comment_at_end(no_cmt1)
    cleaned = clean_str(no_cmt2)
    validated = test_len_error(cleaned)
    try:
        if len(validated) < 7:
            raise ParseError("Missing mandatory parameter!")
        if len(validated) > 7:
            raise ParseError("Too many parameter!")
    except ParseError as e:
        print("Error - ", e)
        os._exit(0)
    as_dict = convert_to_dict(validated)
    final = entry_exit(as_dict)
    is_valid(final)
    return final
