'''
Library to manage software versions. Versions are stored in version.toml inside the current repo.
To update versions interactively, use VersionManager().update_interactive().
'''
import datetime
import json
import pathlib
import urllib.request as urllib

import tomlkit

from github import Github

from bundlewrap.utils import get_file_contents, ErrorContext
from bundlewrap.utils.text import wrap_question, bold, red, green, blue
from bundlewrap.utils.ui import io

class VersionManager:
    '''Manages all software versions'''
    @classmethod
    def _get_versionfile_path(cls):
        path = pathlib.Path(__file__).parent.parent.absolute()
        path = path / "versions.toml"
        return path

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VersionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "toml"):
            return
        try:
            self.toml = tomlkit.parse(get_file_contents(self._get_versionfile_path()))
        except ErrorContext:
            self.toml = tomlkit.toml_document.TOMLDocument()

    def _save(self):
        with open(self._get_versionfile_path(), 'w') as file:
            file.write(tomlkit.dumps(self.toml))

    def _get_version_github(self, repo):
        gh_api = Github()
        gh_repo = gh_api.get_repo(repo)
        latest = gh_repo.get_latest_release()
        return latest.tag_name

    def _get_version_archlinux(self, name):
        url = 'https://www.archlinux.org/packages/search/json/?name={}'.format(name)
        data = json.load(urllib.urlopen(url))
        if len(data['results']) != 1:
            raise Exception("No exact match found for arch package {}".format(name))
        return data['results'][0]['pkgver']

    def _get_version_dummy(self, _):
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def _get_version_gitea(self, url):
        data = json.load(urllib.urlopen(url))
        if len(data) < 1:
            raise Exception("No releases found for gitea url {}".format(url))
        return data[0]['tag_name']

    def _cached_version(self, name):
        if name not in self.toml:
            return None
        if 'version' not in self.toml[name]:
            return None
        return self.toml[name]['version']

    def _latest_version(self, name):
        if name not in self.toml:
            return None
        for key, value in self.toml[name].items():
            if hasattr(self, "_get_version_{}".format(key)):
                return getattr(self, "_get_version_{}".format(key))(value)
        return None

    def add(self, name, **kwargs):
        """Add a new version"""
        table = tomlkit.table()
        if name in self.toml:
            table = self.toml[name].copy()
        # Update version config from kwargs
        for k, value in kwargs.items():
            table[k] = value
        # Check if valid source is configured
        found_source = False
        for key in kwargs:
            if hasattr(self, "_get_version_{}".format(key)):
                found_source = True
                break
        if not found_source:
            raise Exception("No valid version source given for {}".format(name))
        if name not in self.toml:
            self.toml[name] = table
            self.update(name)
        self._save()

    def update(self, name):
        """Update the given version"""
        table = self.toml[name]
        table['version'] = self._latest_version(name)
        table['version_date'] = datetime.datetime.now()
        self._save()

    def get(self, name):
        """Get the currently cached version"""
        return self._cached_version(name)

    def update_interactive(self):
        """Update all versions, prompting the user for each possible update"""
        question = wrap_question(
            bold("Version management"),
            "Do you want to check configured software versions for updates",
            "Check for updates ?",
            prefix="{} versions".format(blue("?")),
        )
        if not io.ask(question, True):
            return
        for name, table in self.toml.items():
            latest = self._latest_version(name)
            current = self._cached_version(name)
            now = datetime.datetime.now()
            if latest == current:
                io.stdout("{x} {name} is up to date ({current})".format(
                    x=green("✓"),
                    name=name,
                    current=current,
                ))
                continue
            question = wrap_question(
                name,
                "{} → {}".format(red(current), green(latest)),
                "Update {}".format(bold(name)),
                prefix="{} versions".format(blue("?"))
            )
            if not io.ask(question, True):
                continue
            table['version'] = latest
            table['version_date'] = now
            self.toml[name] = table
            self._save()

def get(name, **kwargs):
    '''
    Get the current version number for the given software packet. Use additional args to specify
    how the version should be retrieved. Currently supported:
      - `github="<user>/<repo>"`: Get the latest github release
      - `archlinux="<package>"`: Get the current version packaged for archlinux
      - `gitea="https://api/v1/repos/user/name/releases"`: Get the latest gitea release
      - `dummy=""`: A pseudoversion derived from the current date and time
    '''
    VersionManager().add(name, **kwargs)
    return VersionManager().get(name)
