import os
import requests
from microprint_generator import SVGMicroprintGenerator, RasterMicroprintGenerator
from pathlib import Path
import re
import logging


class Api:

    def __init__(self, repo, owner, token):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/actions/"
        self.is_private = self._get_private_status()

    def _get_private_status(self):

        response = requests.get(f"https://api.github.com/repos/{self.owner}/{self.repo}", headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        })

        return response.json()["private"]

    def get(self, url):
        return requests.get(self.base_url + url, headers={
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        })


def get_job_by_name(job_name, job_list):

    for _, job_obj in enumerate(job_list):
        if job_obj["name"] == job_name:
            return job_obj


def get_job_id(api, job_name, run_id):

    all_jobs = api.get(f"runs/{run_id}/jobs").json()

    all_jobs = all_jobs["jobs"]

    job = get_job_by_name(job_name, all_jobs)

    return job["id"]


def setup_api():

    repository = os.environ['INPUT_REPOSITORY'].split("/")

    owner = repository[0]

    repo = repository[1]

    token = os.environ['INPUT_GITHUB_TOKEN']

    return Api(repo, owner, token)


def get_logs(api):

    job_name = os.environ['INPUT_JOB_NAME']

    run_id = os.environ['GITHUB_RUN_ID']

    current_job_id = get_job_id(api, job_name, run_id)

    current_job_logs = api.get(f"jobs/{current_job_id}/logs").text

    save_path = Path(os.environ['INPUT_LOG_PATH']) / \
        (os.environ['INPUT_LOG_FILENAME'] + ".txt")

    if os.environ['INPUT_SAVE_LOG'] == "true":
        with open(save_path, 'w') as file:
            file.write(current_job_logs)

    return current_job_logs


def remove_ansi_escape_sequences(text):

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    return ansi_escape.sub('', text)


def main():
    logging.basicConfig(level=logging.DEBUG)

    api = setup_api()

    logs = get_logs(api)

    logs = remove_ansi_escape_sequences(logs)

    microprint_filename = Path(os.environ['INPUT_MICROPRINT_PATH'])

    if os.environ['INPUT_MICROPRINT_RENDER_METHOD'] == "svg":
        microprint_filename = microprint_filename / \
            (os.environ['INPUT_MICROPRINT_FILENAME'] + ".svg")

        microprint_generator = SVGMicroprintGenerator(
            output_filename=microprint_filename, text=logs)

        microprint_generator.render_microprint()

        if os.environ['INPUT_GENERATE_MICROPRINT_VISUALIZER_LINK']:

            link = "https://api.github.com/repos/owner/repo/contents/path"

            if self.is_private:
                link = link + "?token=" + self.token

            markdown = (
                f"[Look at microprint with Microprint visualizer]({link})")

            markdown_path = Path(os.environ['INPUT_MICROPRINT_VISUALIZER_LINK_PATH']) / Path(
                os.environ['INPUT_MICROPRINT_VISUALIZER_LINK_FILENAME']) + "md"

            Path(markdown_path).write_text(markdown)
    else:
        microprint_filename = microprint_filename / \
            (os.environ['INPUT_MICROPRINT_FILENAME'] + ".png")

        microprint_generator = RasterMicroprintGenerator(
            output_filename=microprint_filename, text=logs)

        microprint_generator.render_microprint()


if __name__ == "__main__":
    main()
