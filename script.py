from ghapi.all import GhApi

def get_logs():

    repository_from_context = env_github.repository.split('/')
    owner = repository_from_context[0]
    repo = repository_from_context[1]
    
    api = GhApi(owner=owner,repo=repo,token=github_token())

    current_job_id = env_github.job
    #run_id = context_github.run_id

    #jobs = api.actions.list_jobs_for_workflow_run_attempt(run_id=run_id)

    print(jobs)

def main():
    get_logs()

if __name__ == "__main__":
    main()

