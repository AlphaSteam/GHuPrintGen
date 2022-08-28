import ghapi.all as ghapi

def get_logs():

    repository = os.environ['INPUT_REPOSITORY'].split("/")
    
    print("repository", repository)

    owner = repository[0]
    print("owner", owner)

    repo = repository[1]
    print("repo", repo)

    token = os.environ['INPUT_GITHUB-TOKEN']

    api = ghapi.GhApi(owner=owner, repo=repo, token=token)

    current_job_id = ghapi.env_github.job
    print("current_job_id", current_job_id)

    try:
        current_job_logs = api.actions.download_job_logs_for_workflow_run(job_id=current_job_id)
        print("current_job_logs", current_job_logs)

    except Exception as e:
        print("Exception", e)

    #run_id = context_github.run_id

    #jobs = api.actions.list_jobs_for_workflow_run_attempt(run_id=run_id)


def main():
    get_logs()

if __name__ == "__main__":
    main()

