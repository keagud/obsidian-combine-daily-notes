#!/bin/env python

import datetime
from contextlib import suppress
from pathlib import Path

import sys


# returns true if the given date is not in the current ongoing week,
# false otherwise
def ok_to_combine(week_start: datetime.date) -> bool:
    today = datetime.date.today()

    #if today is sunday, go ahead and combine anyway
    if today.isoweekday() == 7:
        return True
    
    this_week_start = get_week_start(today)
    return  (this_week_start != week_start)


# given a date, return the date of the previous Monday
def get_week_start(day: datetime.date) -> datetime.date:
    weekday = day.isoweekday()

    while weekday != 1:
        day = day - datetime.timedelta(days=1)
        weekday = day.isoweekday()

    return day


def group_weekly(directory: Path | str = Path.cwd()):
    directory = Path(directory)

    dated_files: list[tuple[Path, datetime.date]] = []

    for file in (dir_item for dir_item in directory.glob("*.md") if dir_item.is_file):
        with suppress(ValueError):
            file_date = datetime.date.fromisoformat(file.stem)
            dated_files.append((file, file_date))

    # group the (file, date) tuples by week
    # dict key is the date of the monday of that week
    week_groups: dict[datetime.date, list[tuple[Path, datetime.date]]] = {}

    for file, file_date in dated_files:
        week_start = get_week_start(file_date)

        if week_start not in week_groups:
            week_groups[week_start] = []

        week_groups[week_start].append((file, file_date))

    # sort the files for each week chronologically, and
    # remove the date entries
    # If a week is still in progress,it is removed

    week_files_grouped: dict[datetime.date, list[Path]] = {
        k: [file for file, _ in sorted(days, key=lambda t: t[1])]
        for k, days in week_groups.items()
        if ok_to_combine(k)
    }

    return week_files_grouped


# condense the given files into a single file
# original file contents are separated by the delimiter parameter
def condense_files(
    combined_filename: str,
    files: list[Path],
    delete_original: bool = True,
    output_dir: Path | str | None = None,
    delimiter: str = "\n---\n",
):
    output_dir = Path.cwd() if output_dir is None else Path(output_dir)
    file_set_content = []

    for file in files:
        section_header = f"## {file.stem}"
        with open(file, "r") as daily_file:
            text_content = daily_file.read()

            if not text_content or text_content.isspace():
                continue

            daily_content = section_header + "\n" + text_content

            file_set_content.append(daily_content)

    combined_content = delimiter.join(file_set_content)
    output_path = output_dir.joinpath(combined_filename)

    if not output_path.suffix:
        output_path = output_path.with_suffix(".md")

    with open(output_path, "w") as outfile:
        outfile.write(combined_content)

    if delete_original:
        [original.unlink() for original in files]


def condense_all_dailies(
    target_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
    clean: bool = True,
):
    target_dir = (
        Path.cwd().joinpath("weekly/") if target_dir is None else Path(target_dir)
    )
    output_dir = Path.cwd() if output_dir is None else Path(output_dir)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    grouped_files = group_weekly(directory=target_dir)

    for start_date, week_files in grouped_files.items():
        combined_filename = f"Week-of-{start_date.isoformat()}.md"
        condense_files(
            combined_filename, week_files, output_dir=output_dir, delete_original=clean
        )


def run():
    clean: bool = False

    try:
        target_dir: str = sys.argv[1]
        output_dir: str = sys.argv[2]

        if len(sys.argv) > 3 and sys.argv[3] == "clean":
            clean = True

    except IndexError as e:
        raise e

    condense_all_dailies(target_dir=target_dir, output_dir=output_dir, clean=clean)

    return 0


if __name__ == "__main__":
    run()
