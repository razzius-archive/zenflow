#!/usr/bin/env python3.5

import aiohttp
import argparse
import asyncio
import os


async def get_milestones(client):
    async with client.get(
        'https://api.github.com/repos/sighten/clint/milestones',
        headers={
            'Authorization': 'Token {}'.format(os.environ['GITHUB_API_TOKEN'])
        }
    ) as response:
        return await response.json()


async def get_milestone_by_name(loop, verbosity, milestone_name):
    with aiohttp.ClientSession(loop=loop) as client:
        milestones = await get_milestones(client)

        if verbosity:
            print('Milestones:')
            print(milestones)

        milestone_number_dict = {milestone['title']: milestone['number'] for milestone in milestones}
        return milestone_number_dict[milestone_name]


async def main(milestone, verbosity=0):
    milestone_number = await get_milestone_by_name(loop, verbosity, milestone)

    print(milestone_number)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('milestone')
    parser.add_argument('-v', '--verbosity',
                        action='count')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.milestone, args.verbosity))
