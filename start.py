#!/usr/bin/env python3.5

from lib import (
    PIPELINE_IDS,
    async_execute,
    get_top_issue_by_pipeline,
    change_issue_pipeline
)


async def main(loop):
    issue_number = await get_top_issue_by_pipeline(loop, 'backlog', 'razzius', 'v1.17')

    print('Moving issue {} to "In Development"'.format(issue_number))

    response = await change_issue_pipeline(loop,
                                           issue_number,
                                           PIPELINE_IDS['backlog'],
                                           PIPELINE_IDS['in_development'])

    # todo parse the output
    print(response)

if __name__ == '__main__':
    async_execute(main)
