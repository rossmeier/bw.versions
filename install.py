#!/bin/python

import os
import pathlib
import sys

from bundlewrap.exceptions import NoSuchRepository
from bundlewrap.repo import Repository
from bundlewrap.utils.ui import io
from bundlewrap.utils.text import red, yellow, bold, green

def install_dir(source, target):
    relpath = os.path.relpath(source, target)
    for _, dirs, files in os.walk(source, topdown=True):
        for directory in dirs:
            os.mkdir(target / directory)
        for file in files:
            try:
                os.symlink(
                    os.path.join(relpath, file),
                    os.path.join(target, file),
                )
            except FileExistsError:
                pass
            io.stdout("{} installed {}".format(
                green("✓"),
                bold(os.path.join(os.path.basename(target), file)),
            ))

def main():
    io.activate()
    try:
        repo = Repository("")
    except NoSuchRepository:
        io.stderr("{} Not inside a bundlewrap repository".format(red("!")))
        sys.exit(1)
    my_path = pathlib.Path(__file__).parent.absolute()
    relpath = my_path.relative_to(repo.path)
    if not str(relpath).startswith("collections/"):
        io.stderr("{} Collection should be installed to <repo>/collections".format(yellow("!")))
        sys.exit(1)
    install_dir(my_path / "hooks", repo.hooks_dir)
    install_dir(my_path / "libs", repo.libs_dir)
    install_dir(my_path / "items", repo.items_dir)

if __name__ == "__main__":
    main()
