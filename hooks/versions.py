'''
Included hooks for the versions collection
'''

from bundlewrap.utils.text import wrap_question, bold, blue
from bundlewrap.utils.ui import io

def apply_start(repo, target, nodes, interactive=False, **kwargs):
    '''
    Interactively update all versions if running in interactive mode.
    '''
    _ = target
    _ = nodes
    _ = kwargs
    if interactive:
        question = wrap_question(
            bold("Version management"),
            "Do you want to check configured software versions for updates",
            "Check for updates ?",
            prefix="{} versions".format(blue("?")),
        )
        if not io.ask(question, True):
            return
        repo.libs.versions.VersionManager().update_all(interactive=True)
