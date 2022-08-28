import ghapi.all as ghapi
import os
from jsonref import loads

def get_job_by_name(job_name, job_list):

    for _, job_obj in enumerate(job_list):
        if job_obj["name"] == job_name:
            return job_obj


def get_job_id(api, job_name, run_id):

    all_jobs = api.actions.list_jobs_for_workflow_run(run_id=run_id)["jobs"]

    job = get_job_by_name(job_name, all_jobs)

    return job["id"]

    
def get_logs():

    repository = os.environ['INPUT_REPOSITORY'].split("/")
    
    owner = repository[0]

    repo = repository[1]

    token = os.environ['INPUT_GITHUB-TOKEN']

    api = ghapi.GhApi(owner=owner, repo=repo, token=token)

    job_name = ghapi.env_github.job

    run_id = ghapi.env_github.run_id

    current_job_id = get_job_id(api, job_name, run_id)
    
    current_job_logs = api.actions.download_job_logs_for_workflow_run(job_id=current_job_id)
    
    print("current_job_logs", loads(current_job_logs))

    

def main():
    try:
        get_logs()
    except Exception as e:
        print("Exception", e)

if __name__ == "__main__":
    main()

