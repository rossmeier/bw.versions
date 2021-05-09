# bw.versions
Easy versions management for bundlewrap.

## Installation
Run the folowing inside your bundlewrap repo:
```bash
mkdir collections
cd collections
git submodule add https://github.com/veecue/bw.versions
./bw.versions/install.py
```
This will install this collections to `collections/bw.versions` and create appropriate symlinks for all the files.
Then commit all created files to your repository.

## Usage
To get the latest version of some software you want to install, simply use `repo.libs.versions.get()`.

Example for a bundle downloading the latest version of gitea:
```python
version = repo.libs.versions.get("gitea", github="go-gitea/gitea").lstrip("v")
actions = {
    'download': {
        'unless': 'test -f /root/gitea-{}-linux-amd64').format(version),
        'command': 'curl -fsSL -o /root/gitea-{version}-linux-amd64 '
            'https://dl.gitea.io/gitea/{version}/gitea-{version}-linux-amd64;'
            'chmod 755 /root/gitea-{version}-linux-amd64').format(
                version=version,
            ),
    },
}
```

### Upstream version source
You can specify where the version should be retrieved from by using args to `versions.get()`. Currently supported:
 - `github="<user>/<repo>"`: Get the latest github release
 - `archlinux="<package>"`: Get the current version packaged for archlinux
 - `dummy=""`: A pseudoversion derived from the current date and time

### Updating versions
Thanks to the integrated `apply_start()` hook, the user will automatically be asked to update versions for each run of
`bw apply -i`. This will look like the following:
```
➜  bw git:(master) $ bw apply -i gitea
? versions
? versions ╭─ Version management
? versions │
? versions │  Do you want to check configured software versions for updates
? versions │
? versions ╰─ Check for updates ? [Y/n] Y
✓ gitea is up to date (v1.12.4)
? versions
? versions ╭─ bla
? versions │
? versions │  20200926150619 → 20200926152325
? versions │
? versions ╰─ Update bla [Y/n] n
```

### Version cache
The current version for each software will be stored to `versions.toml` inside your repo. Depending on your workflow,
you can either add this to your `.gitignore` or commit it to your repo.
