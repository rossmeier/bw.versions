'''
Included hooks for the versions collection
'''

def apply_start(repo, target, nodes, interactive=False, **kwargs):
    '''
    Interactively update all versions if running in interactive mode.
    '''
    _ = target
    _ = nodes
    _ = kwargs
    if interactive:
        repo.libs.versions.VersionManager().update_interactive()
