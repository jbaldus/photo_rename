#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime
import logging

import exifread

logging.basicConfig()
logging.setLevel(logging.CRITICAL)


file_name_format = "%Y%m%d_%H%M%S"

def uniquify(path:Path, sep='_') -> Path:
    path = Path(path)
    parent = path.parent
    stem = path.stem
    suffixes = path.suffixes
    counter = 1
    if not path.exists():
        return path
    while True:
        new_path = parent / f"{stem}{sep}{counter}{''.join(suffixes)}"
        if not new_path.exists():
            return new_path
        counter += 1

def get_tags(image_path:Path) -> dict:
    with open(image_path, 'rb') as f:
        t = exifread.process_file(f)
    return t

def rename(path:Path, new_path:Path, not_really = False) -> Path:
    if new_path == path:
        logging.warning(f"Not Renaming {path} to {new_path}, they're the same.")
        return path
    adjusted_new_path = uniquify(new_path)
    if not_really:
        print(f"Would rename {path} -> {adjusted_new_path}")
    else:
        logging.warning(f"Actually renaming {path} -> {adjusted_new_path}")
        return path.rename(adjusted_new_path)

def try_rename(path:Path, tags:dict, not_really = False) -> Path:
    global file_name_format
    exif_time_format = "%Y:%m:%d %H:%M:%S"
    dt = None
    if "EXIF DateTimeOriginal" in tags:
        dt = tags["EXIF DateTimeOriginal"].values
    elif "Image DateTime" in tags:
        dt = tags["Image DateTime"].values
    date_tags = [k for k in tags.keys() if 'Date' in k]
    if dt is None:
        logging.info(f"Could not find date information for {path}.")
        if date_tags:
            logging.info(f"Would any of these work: {date_tags}?")
        return None
    dt = datetime.strptime(dt, exif_time_format)
    new_stem = dt.strftime(file_name_format)
    return rename(path, path.parent / (new_stem + ''.join(path.suffixes)), not_really)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", default=[], type=str)
    parser.add_argument("-n", "--not-really", action="store_true")
    parser.add_argument("-v", "--verbose", action='count', default=0)

    args = parser.parse_args()

    log_levels = [logging.CRITICAL, logging.WARNING, logging.INFO, logging.DEBUG]
    logging.setLevel(log_levels[min((args.verbose, len(log_levels)-1))])

    for f in args.files:
        path = Path(f)
        try_rename(path, get_tags(path), not_really=args.not_really)
            
