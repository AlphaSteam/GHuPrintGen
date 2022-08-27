import ghapi.all as ghapi

def get_logs():

    repository_from_context = ghapi.env_github.repository.split('/')
    owner = repository_from_context[0]
    repo = repository_from_context[1]
    
    api = ghapi.GhApi(owner=owner,repo=repo,token=github_token())

    current_job_id = ghapi.env_github.job

    current_job_logs = api.actions.download_job_logs_for_workflow_run(current_job_id)

    print(current_job_logs)
    #run_id = context_github.run_id

    #jobs = api.actions.list_jobs_for_workflow_run_attempt(run_id=run_id)


def main():
    get_logs()

if __name__ == "__main__":
    main()

