#!/usr/bin/env python3.5

import os

from lib import get_top_issue_by_pipeline, async_execute


async def main(loop):
    milestone_name = os.environ['GITHUB_MILESTONE']
    print(await get_top_issue_by_pipeline(loop, 'in_development', 'razzius', milestone_name))


if __name__ == '__main__':
    async_execute(main)
