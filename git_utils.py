import os

from pygit2 import Repository


def push_current_branch():
    # TODO use pygit2
    os.system('git push')


def get_current_branch_name():
    repository = Repository('.')
    return repository.head.shorthand


def checkout_new_branch(branch_name):
    repository = Repository('.')

    if not repository.lookup_branch(branch_name):
        repository.create_branch(branch_name, repository.head.get_object())  # todo use develop as base

    branch = repository.lookup_branch(branch_name)
    print(branch.name)
    branch_ref = repository.lookup_reference(branch.name)
    repository.checkout_tree(branch_ref)
