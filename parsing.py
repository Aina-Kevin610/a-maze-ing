import os
import random
from typing import Any
from render_terminal import print_box


class ParseError(Exception):

    def __init__(self, msg: str = "Invalid config format!") -> None:
        super().__init__(msg)


def read_file(filename: str) -> list[str]:
    content: list[str] = []

    try:
        if filename != "config.txt":
            raise ParseError("Invalid filename!")

        with open(filename, "r", encoding="utf-8") as file:
            content = file.read().strip().splitlines()

    except ParseError as error:
        print("Error -", error)

    except FileNotFoundError:
        print("Error - File not found!")

    return content


def remove_space(content: list[str]) -> list[str]:
    return [line for line in content if line != ""]


def comment_at_first(content: list[str]) -> list[str]:
    return [line for line in content if not line.startswith("#")]


def comment_at_end(content: list[str]) -> list[list[str]]:
    stripped = [line.strip() for line in content]
    split_lines = [line.split("#", maxsplit=1) for line in stripped]

    return split_lines


def clean_str(content: list[list[str]]) -> list[str]:
    result: list[str] = []

    for item in content:
        cleaned = item[0].strip()
        result.append(cleaned)

    return result


def test_len_error(content: list[str]) -> list[tuple[str, str]]:
    tuples: list[tuple[str, str]] = []

    try:
        for line in content:
            split_line = line.replace(" ", "").split("=")

            if len(split_line) != 2:
                raise ParseError("Invalid config format!")

            tuples.append((split_line[0], split_line[1]))

        return tuples

    except ParseError as error:
        print("Error -", error)
        os._exit(0)


def convert_to_dict(content: list[tuple[str, str]]) -> dict[str, str]:
    return {key: value.strip() for key, value in content}


def entry_exit(new_content: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = dict(new_content)

    result["ENTRY"] = tuple(new_content["ENTRY"].split(","))
    result["EXIT"] = tuple(new_content["EXIT"].split(","))

    return result


def is_valid(final: dict[str, Any]) -> None:
    algos = [
        "DFS",
        "hunt_and_kill",
        "backtracking",
        "prim",
    ]

    mandatory_keys = [
        "HEIGHT",
        "WIDTH",
        "ENTRY",
        "EXIT",
        "PERFECT",
        "OUTPUT_FILE",
    ]

    try:
        for key in mandatory_keys:
            if key not in final:
                raise ParseError(f"Missing mandatory config [{key}]")

        if "ALGO" not in final:
            final["ALGO"] = random.choice(algos)

        if "SEED" not in final:
            final["SEED"] = None

        width = int(final["WIDTH"])
        height = int(final["HEIGHT"])

        entry_x = int(final["ENTRY"][0])
        entry_y = int(final["ENTRY"][1])

        exit_x = int(final["EXIT"][0])
        exit_y = int(final["EXIT"][1])

        if width < 3 or height < 3:
            raise ParseError(
                "Too small HEIGHT or WIDTH (minimum: 3 x 3)!"
            )

        if not final["OUTPUT_FILE"].endswith(".txt"):
            raise ParseError(
                "OUTPUT_FILE extension must be '.txt'!"
            )

        if final["PERFECT"] not in ("True", "False"):
            raise ParseError(
                "PERFECT option must be boolean!"
            )

        if final["ALGO"] not in algos:
            raise ParseError(
                f"Unknown parameter for ALGO! "
                f"Algo must be {algos}"
            )

        if len(final["ENTRY"]) != 2:
            raise ParseError("Invalid ENTRY parameter!")

        if len(final["EXIT"]) != 2:
            raise ParseError("Invalid EXIT parameter!")

        if not (0 <= entry_x < width):
            raise ParseError("Entry point out of range!")

        if not (0 <= entry_y < height):
            raise ParseError("Entry point out of range!")

        if not (0 <= exit_x < width):
            raise ParseError("Exit point out of range!")

        if not (0 <= exit_y < height):
            raise ParseError("Exit point out of range!")

        if final["ENTRY"] == final["EXIT"]:
            raise ParseError(
                "ENTRY and EXIT cannot be at the same position!"
            )

    except (ValueError, ParseError) as error:
        print("Error -", error)
        os._exit(0)


def parse_config(
    filename: str = "config.txt",
) -> dict[str, Any]:
    content = read_file(filename)

    no_space = remove_space(content)
    no_comment_start = comment_at_first(no_space)
    no_comment_end = comment_at_end(no_comment_start)

    cleaned = clean_str(no_comment_end)

    validated = test_len_error(cleaned)

    if len(validated) < 6:
        print("Error - Missing mandatory parameter!")
        os._exit(0)

    as_dict = convert_to_dict(validated)

    final = entry_exit(as_dict)

    is_valid(final)

    if "PATTERN" not in final:
        final["PATTERN"] = "42"

    return final
