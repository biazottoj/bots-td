import requests
from pathlib import Path
import os
import json
from time import time, sleep

class GHRequestsBots():
    def __init__(self, token=None, api_url='https://api.github.com', cache_dir=None, bot=None, results_per_page=None):
        self.token = token
        self.api_url = api_url
        self.bot = bot
        self.per_page = results_per_page
        self.cache_dir = Path(cache_dir if cache_dir else tempfile.mkdtemp())

    @staticmethod
    def _sleep_if_necessary(r):
        """
        Sleep if necessary
        :return:
        """
        print('Limit remaining: {}'.format(r.headers['X-RateLimit-Remaining']))
        sleep_time = float(r.headers['X-RateLimit-Reset']) - time()
        print('Time to reset: {0:.1f}s\n'.format(sleep_time))
        if int(r.headers['X-RateLimit-Remaining']) <= 0:
            print('Sleep for {0:.1f}s...'.format(sleep_time))
            sleep(sleep_time)
    
    def _get_issue_pages(self):
        headers = {"accept": "application/vnd.github.v3+json",
                   "authorization": f"token {self.token}"}
        url = f'https://api.github.com/search/issues?q=involves:{self.bot}+is:issue'
        response = requests.get(url, headers).json()
        n_results = 0
        if 'total_count' in response.keys():
            n_results= response['total_count']
            
        n_pages = int(n_results / 100)
        if n_results < (n_pages * 100):
            n_pages += 1
        return n_pages 
    
    def _get_comment_count(comments_link = None):
        headers = {"accept": "application/vnd.github.v3+json",
                   "authorization": f"token {self.token}"}
        return requests.get(query_issue_url, headers=headers, params=params)

    def get_issues_per_bot(self):
        headers = {"accept": "application/vnd.github.v3+json",
                   "authorization": f"token {self.token}"}
        n_pages = self._get_issue_pages()
        for page in range(1, (n_pages if n_pages <= 10 else 10) + 1):
            page_path = self.cache_dir.joinpath(self.bot).joinpath('issues').joinpath(str(page))
            if not page_path.exists():
                params = {'page': f'{page}', 'per_page': f'{self.per_page}'}
                query_issue_url = f'https://api.github.com/search/issues?q=involves:{self.bot}+is:issue'
                rs = requests.get(query_issue_url, headers=headers, params=params)
                issue_list = rs.json()
                if 'items' in issue_list.keys():
                    for issue in issue_list['items']:
                        issue_path = page_path.joinpath(str(issue['number']))
                        issue_path.mkdir(parents=True, exist_ok=True)
                        with open(issue_path.joinpath('json'), 'w') as f:
                            json.dump(issue, f)
                        comments = requests.get(issue['comments_url'], headers=headers).json()
                        comments_path = issue_path.joinpath('comments')
                        comments_path.mkdir(parents=True, exist_ok=True)
                        for c in comments:
                            try:
                                with open(comments_path.joinpath(f'{c["id"]}.json'), 'w') as f:
                                    json.dump(c, f)
                            except:
                                pass
                else:
                    print(issue_list)
                self._sleep_if_necessary(rs)