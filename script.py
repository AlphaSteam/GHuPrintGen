import os
from pathlib import Path
import requests
import re
import logging
import json
from uprintgen import SVGMicroprintGenerator


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


def append_matrix_values(string, matrix_values, with_spaces=False):

    if matrix_values != None and matrix_values != "":
        matrix_values = matrix_values.values()

        if len(matrix_values) > 0:
            string += f" (" + ', '.join(
                map(str, matrix_values)) + ")"

    if with_spaces == False:
        string = string.replace(" ", "")

    return string


def get_job_id(api, matrix_values):

    job_name = os.environ['INPUT_JOB_NAME']

    run_id = os.environ['GITHUB_RUN_ID']

    job_name = append_matrix_values(
        job_name, matrix_values, with_spaces=True)

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

    if os.environ['INPUT_SAVE_LOG'] == "true":
        directory_path = Path(os.environ['INPUT_LOG_PATH'])
        save_path = directory_path / \
            Path(append_matrix_values(
                os.environ['INPUT_LOG_FILENAME'], matrix_values) + ".txt")

        try:
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
        except Exception as e:
            print(
                f"Directory: {directory_path} couldn't be created. Error: {e}")

        with open(save_path, 'w') as file:
            file.write(current_job_logs)

    return current_job_logs


def generate_visualizer_link(api, microprint_filename, matrix_values):
    microprint_visualizer_page = "https://alphasteam.github.io/uPrintVis/"

    link = f"{microprint_visualizer_page}?url=https://api.github.com/repos/{api.owner}/{api.repo}/contents/{microprint_filename}&ref={api.ref}"

    if api.is_private:
        link = link + "&token=" + api.token

    markdown = (
        f"[Look at microprint with Microprint visualizer]({link})")

    directory_path = Path(os.environ['INPUT_MICROPRINT_VISUALIZER_LINK_PATH'])

    markdown_path = directory_path / Path(append_matrix_values(
        os.environ['INPUT_MICROPRINT_VISUALIZER_LINK_FILENAME'], matrix_values) + ".md")

    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except Exception as exception:
        print(f"Directory: {directory_path} couldn't be created. Error: {exception}")

    Path(markdown_path).write_text(markdown)


def main():
    logging.basicConfig(level=logging.DEBUG)

    api = setup_api()

    matrix_values = os.environ.get("INPUT_MATRIX", None)

    if matrix_values != None and matrix_values != "":
        try:
            matrix_values = json.loads(matrix_values)
        except Exception as e:
            pass

    logs = get_logs(api, matrix_values)

    directory_path = Path(os.environ['INPUT_MICROPRINT_PATH'])

    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except Exception as exception:
        print(
            f"Directory: {directory_path} couldn't be created. Error: {exception}")

    microprint_filename = directory_path / \
        Path(append_matrix_values(
            os.environ['INPUT_MICROPRINT_FILENAME'], matrix_values) + ".svg")

    config_path = Path(os.environ['INPUT_MICROPRINT_CONFIG_PATH'])
    config_filename = (
        os.environ['INPUT_MICROPRINT_CONFIG_FILENAME'] + ".json")

    config_file_path = config_path / config_filename

    microprint_generator = SVGMicroprintGenerator(
        output_filename=microprint_filename, text=logs, config_file_path=config_file_path)

    microprint_generator.render_microprint()

    if os.environ['INPUT_GENERATE_MICROPRINT_VISUALIZER_LINK']:
        generate_visualizer_link(api, microprint_filename, matrix_values)


if __name__ == "__main__":
    main()
