import requests
import json
import argparse


def closed_pulls(branch):
    params = {
        'state': 'closed',
        'base': branch
    }
    response = requests.get('https://api.github.com/repos/ansible/galaxy/pulls', params=params)
    for issue in response.json():
        print("- `{} {} <{}>`_".format(issue['number'], issue['title'], issue['html_url']))

def main():
    parser = argparse.ArgumentParser(description='List closed pull requests.') 
    parser.add_argument('branch', help='Branch name from which to list closed PRs') 
    args = parser.parse_args()
    print("\nClosed pull requests:")
    closed_pulls(args.branch)

if __name__ == '__main__':
    main()
