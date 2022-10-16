import os
import requests
from microprint_generator import SVGMicroprintGenerator, RasterMicroprintGenerator
from pathlib import Path
import re
import logging
import json


class Api:

    def __init__(self, repo, owner, token, ref):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.ref = ref
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


def append_matrix_values(string, matrix_values):
    if matrix_values != None and matrix_values != "":
        matrix_values = matrix_values.values()

        if len(matrix_values) > 0:
            string += " (" + ', '.join(map(str, matrix_values)) + ")"

    return string


def get_job_id(api, matrix_values):

    job_name = os.environ['INPUT_JOB_NAME']

    run_id = os.environ['GITHUB_RUN_ID']

    job_id = os.environ['INPUT_JOB_ID']

    if matrix_values != None and matrix_values != "":
        try:
            matrix_values = json.loads(matrix_values)
        except e:
            pass

    if job_id != None and job_id != "":
        # TODO add matrix values to job_id
        current_job_id = job_id
    else:
        job_name = append_matrix_values(job_name, matrix_values)

        all_jobs = api.get(f"runs/{run_id}/jobs").json()

        all_jobs = all_jobs["jobs"]

        job = get_job_by_name(job_name, all_jobs)

        current_job_id = job["id"]

    return current_job_id


def setup_api():

    repository = os.environ['INPUT_REPOSITORY'].split("/")

    owner = repository[0]

    repo = repository[1]

    token = os.environ['INPUT_GITHUB_TOKEN']

    ref = os.environ['INPUT_REF']

    return Api(repo, owner, token, ref)


def get_logs(api, matrix_values):

    job_id = get_job_id(api, matrix_values)

    current_job_logs = api.get(f"jobs/{job_id}/logs").text

    save_path = Path(append_matrix_values(os.environ['INPUT_LOG_PATH'], matrix_values)) / \
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

    matrix_values = os.environ.get("INPUT_MATRIX", None)

    logs = get_logs(api, matrix_values)

    logs = remove_ansi_escape_sequences(logs)

    microprint_filename = Path(append_matrix_values(
        os.environ['INPUT_MICROPRINT_PATH'], matrix_values))

    if os.environ['INPUT_MICROPRINT_RENDER_METHOD'] == "svg":
        microprint_filename = microprint_filename / \
            (os.environ['INPUT_MICROPRINT_FILENAME'] + ".svg")

        microprint_generator = SVGMicroprintGenerator(
            output_filename=microprint_filename, text=logs)

        microprint_generator.render_microprint()

        if os.environ['INPUT_GENERATE_MICROPRINT_VISUALIZER_LINK']:
            microprint_visualizer_page = "https://alphasteam.github.io/microprint-visualizer/"

            link = f"{microprint_visualizer_page}?url=https://api.github.com/repos/{api.owner}/{api.repo}/contents/{microprint_filename}&ref={api.ref}"

            if api.is_private:
                link = link + "&token=" + api.token

            markdown = (
                f"[Look at microprint with Microprint visualizer]({link})")

            markdown_path = Path(append_matrix_values(
                os.environ['INPUT_MICROPRINT_VISUALIZER_LINK_PATH'], matrix_values)) / Path(
                os.environ['INPUT_MICROPRINT_VISUALIZER_LINK_FILENAME'] + ".md")

            Path(markdown_path).write_text(markdown)
    else:
        microprint_filename = microprint_filename / \
            (os.environ['INPUT_MICROPRINT_FILENAME'] + ".png")

        microprint_generator = RasterMicroprintGenerator(
            output_filename=microprint_filename, text=logs)

        microprint_generator.render_microprint()


if __name__ == "__main__":
    main()
