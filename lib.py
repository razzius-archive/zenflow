import logging
import os
import asyncio

import aiohttp
import requests


logger = logging.getLogger()
# logger.setLevel('DEBUG')


# todo move to constants.py
PIPELINE_IDS = {
    'new_issues': '54c19ad8f748cd180f07b4b7',
    'backlog': '54c19ad8f748cd180f07b4b6',
    'in_development': '54c19ad8f748cd180f07b4b4',
    'pr_outstanding': '55c2c7964e6d61ea173a1ce8'
}

MILESTONE_IDS = {
    'v1.17': 85,
    'v1.18': 88,
    'v1.19': 91,
    'v1.20': 95,
    'v1.21': 99,
    'v1.22': 102
}


CLINT_REPO_ID = '14154595'


async def _get_zenhub_issues(client):
    async with client.get('https://api.zenhub.io/p1/repositories/14154595/board', headers={
        'X-Authentication-Token': os.environ['ZENHUB_API_TOKEN']
    }) as response:
        return await response.json()


async def _get_github_issues(client, assignee, milestone_id):
    async with client.get(
        'https://api.github.com/repos/sighten/clint/issues',
        headers={
            'Authorization': 'Token {}'.format(os.environ['GITHUB_API_TOKEN'])
        },
        params={
            'assignee': assignee,
            'milestone': milestone_id
        }
    ) as response:
        return await response.json()


async def _zenhub_issue_numbers(loop, pipeline_name):
    """Returns a list of issue numbers ordered by ZenHub board position (indicates priority)."""
    with aiohttp.ClientSession(loop=loop) as client:
        content = await _get_zenhub_issues(client)

    in_development = next(
        p for p in content['pipelines']
        if p['name'].lower().replace(' ', '_').startswith(pipeline_name)
    )

    return [issue['issue_number'] for issue in in_development['issues']]


async def _github_issue_numbers(loop, assignee, milestone_id):
    with aiohttp.ClientSession(loop=loop) as client:
        content = await _get_github_issues(client, assignee, milestone_id)

    return {
        issue['number'] for issue in content
    }


async def get_top_issue_by_pipeline(loop, pipeline_name, username, milestone_number):
    zenhub_priorities = await _zenhub_issue_numbers(loop, pipeline_name)
    github_issues = await _github_issue_numbers(loop, username, MILESTONE_IDS[milestone_number])

    logger.debug('Zenhub priorities:')
    logger.debug(zenhub_priorities)

    logger.debug('Github issues:')
    logger.debug(github_issues)

    return next(
        issue for issue in zenhub_priorities
        if issue in github_issues
    )


async def change_issue_pipeline(loop, issue_number, from_pipeline_id, to_pipeline_id):
    # todo do I need to pass the from_pipeline_id
    # TODO do I need to pass the issue ID in the url and body?

    api_url = 'https://api.zenhub.io/v3/repositories/{}/issues/{}/pipelines'.format(
        CLINT_REPO_ID, issue_number)

    with aiohttp.ClientSession(loop=loop) as client:
        return await client.put(
        api_url,
        headers={
            'x-authentication-token': os.environ['ZENHUB_INTERNAL_API_TOKEN']
        },
        data={
            'issue_number': issue_number,
            'repo_id': CLINT_REPO_ID,
            'from_pipeline_id': PIPELINE_IDS['backlog'],
            'pipeline_id': PIPELINE_IDS['in_development']
        }
    )


def async_execute(main_function, *main_args, **main_kwargs):
    """Run an asynchronous main function."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_function(loop, *main_args, **main_kwargs))
