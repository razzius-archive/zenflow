#!/usr/bin/env python3.5

import os

from lib import (
    PIPELINE_IDS,
    async_execute,
    get_top_issue_by_pipeline,
    change_issue_pipeline
)

from git_utils import checkout_new_branch


async def main(loop):
    milestone_name = os.environ['GITHUB_MILESTONE']
    issue_number = await get_top_issue_by_pipeline(loop, 'backlog', 'razzius', milestone_name)

    print('Moving issue {} to "In Development"'.format(issue_number))

    response = await change_issue_pipeline(loop,
                                           issue_number,
                                           PIPELINE_IDS['backlog'],
                                           PIPELINE_IDS['in_development'])

    # todo parse the output
    print(response)

    checkout_new_branch('razzi/{}'.format(issue_number))


if __name__ == '__main__':
    async_execute(main)
