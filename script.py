import os
import json
import requests


class Api:

    def __init__(self, repo, owner, token):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/actions/"

    def get(self, url):
        return requests.get(self.base_url + url, headers={
                "Authorization": f"token {self.token}"
            })

def get_job_by_name(job_name, job_list):

    for _, job_obj in enumerate(job_list):
        if job_obj["name"] == job_name:
            return job_obj


def get_job_id(api, job_name, run_id):

    all_jobs = json.loads(api.get(f"runs/{run_id}/jobs"))["jobs"]

    job = get_job_by_name(job_name, all_jobs)

    return job["id"]


def setup_api():

    repository = os.environ['INPUT_REPOSITORY'].split("/")
    
    owner = repository[0]

    repo = repository[1]

    token = os.environ['INPUT_GITHUB-TOKEN']

    return Api(repo, owner, token)


def get_logs(api):

    job_name = os.environ['GITHUB_JOB']

    run_id = os.environ['GITHUB_RUN_ID']

    current_job_id = get_job_id(api, job_name, run_id)
    
    current_job_logs = api.get(f"jobs/{current_job_id}/logs")

    print(current_job_logs)    
    

def main():
    api = setup_api()

    get_logs(api)


if __name__ == "__main__":
    main()

