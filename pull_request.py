#!/usr/bin/env python3.5

"""
Make the PR
Move the current branch's issue to PR outstanding
Move the PR's issue to PR outstanding
goonies label (?)
add to sprint
assign somebody
run next?
"""

import argparse
import json
import os

import aiohttp
from lib import async_execute, CLINT_REPO_ID, PIPELINE_IDS
from git_utils import get_current_branch_name


def _get_issue_number(branch_name):
    return branch_name.split('/')[-1]


async def create_pull_request(client,
                              base_branch,
                              title_text,
                              branch_name):
    issue_number = _get_issue_number(branch_name)

    title = '{} {} -> {}'.format(branch_name, title_text, base_branch)
    body = '#{}'.format(issue_number)

    return await client.post(
        'https://api.github.com/repos/sighten/clint/pulls',
        headers={
            'Authorization': 'Token {}'.format(os.environ['GITHUB_API_TOKEN']),
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            'title': title,
            'head': branch_name,
            'base': base_branch,
            'body': body
        })
    )


async def move_ticket_to_pr_outstanding(client, issue_number):
    return await client.put(
        'https://api.zenhub.io/v3/repositories/{}/issues/{}/pipelines'
        .format(CLINT_REPO_ID, issue_number),
        headers={
            'x-authentication-token': os.environ['ZENHUB_INTERNAL_API_TOKEN']
        },
        data={
            'issue_number': issue_number,
            'repo_id': CLINT_REPO_ID,
            'from_pipeline_id': PIPELINE_IDS['in_development'],
            'pipeline_id': PIPELINE_IDS['pr_outstanding']
        }
    )


async def move_ticket_pipeline(client, ticket_number, from_pipeline, to_pipeline):
    async with client.put(
        'https://api.zenhub.io/v3/repositories/{}/issues/{}/pipelines'
        .format(CLINT_REPO_ID, ticket_number),
        headers={
            'x-authentication-token': os.environ['ZENHUB_INTERNAL_API_TOKEN']
        },
        data={
            'issue_number': ticket_number,
            'repo_id': CLINT_REPO_ID,
            'from_pipeline_id': PIPELINE_IDS[from_pipeline],
            'pipeline_id': PIPELINE_IDS[to_pipeline]
        }
    ) as response:
        return await response.read()


async def main(loop, base_branch, title, assignee):
    print('Creating PR with text "{}" into {}'.format(title_text, base_branch))

    branch_name = get_current_branch_name()
    issue_number = _get_issue_number(branch_name)

    with aiohttp.ClientSession(loop=loop) as client:
        github_response = await create_pull_request(client, base_branch, title, branch_name)
        print('Create PR status: {}'.format(github_response.status))

        github_json = await github_response.json()

        move_ticket_resp = await move_ticket_to_pr_outstanding(client, issue_number)
        print('Move ticket to PR outstanding: {}'.format(move_ticket_resp.status))

        pr_number = github_json['number']

        move_pr_resp = await move_ticket_pipeline(client, pr_number, 'new_issues', 'pr_outstanding')
        print('Move pr to PR outstanding: {}'.format(move_pr_resp))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--assign')
    parser.add_argument('-b', '--base', default='develop')
    parser.add_argument('title', nargs='+')

    args = parser.parse_args()

    title_text = ' '.join(args.title)

    async_execute(main, args.base, title_text, args.assign)
