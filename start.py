#!/usr/bin/env python3.5

# TODO this is copypasta

import aiohttp
import argparse
import asyncio
import os


async def get_zenhub_issues(client):
    async with client.get('https://api.zenhub.io/p1/repositories/14154595/board', headers={
        'X-Authentication-Token': os.environ['ZENHUB_API_TOKEN']
    }) as response:
        return await response.json()


async def get_github_issues(client):
    async with client.get(
        'https://api.github.com/repos/sighten/clint/issues',
        headers={
            'Authorization': 'Token {}'.format(os.environ['GITHUB_API_TOKEN'])
        },
        params={
            'milestone': 82,
            'assignee': 'razzius'
        }
    ) as response:
        return await response.json()


def parse_zenhub_issue_numbers(content):
    """Returns a list of issue numbers ordered by ZenHub board position (indicates priority)."""
    in_development = next(
        p for p in content['pipelines']
        if p['name'].startswith('Backlog')
    )

    return [x['issue_number'] for x in in_development['issues']]


def parse_github_issue_numbers(content):
    return {issue['number'] for issue in content}


async def get_issue_numbers(loop):
    with aiohttp.ClientSession(loop=loop) as client:
        content = await get_zenhub_issues(client)
        issue_numbers = parse_zenhub_issue_numbers(content)
        return issue_numbers


async def get_my_issues(loop):
    with aiohttp.ClientSession(loop=loop) as client:
        content = await get_github_issues(client)
        issue_numbers = parse_github_issue_numbers(content)
        return issue_numbers


async def main(verbosity=0):
    zenhub_priorities = await get_issue_numbers(loop)
    github_issues = await get_my_issues(loop)

    if verbosity:
        print('Zenhub priorities:')
        print(zenhub_priorities)

        print('Github issues:')
        print(github_issues)

    target = next(
        issue for issue in zenhub_priorities
        if issue in github_issues
    )

    print('Moving issue {} to "In Development"'
          .format(target))

    # TODO do I need to pass the issue ID in the url and body?
    requests.post('https://api.zenhub.io/v3/repositories/14154595/issues/{}/pipelines', params={
        'issue_number': target,
        'repo_id': 14154595,
        'pipeline_id': '54c19ad8f748cd180f07b4b6',
        # 'issue_title': ??
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbosity',
                        help='print debug information',
                        default=0,
                        action='count')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.verbosity))
