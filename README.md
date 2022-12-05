# Generate a microprint of the logs of a workflow job

The action generates a highly microprint of the logs generated by a job inside a Github workflow.

If the job hasn't finished yet, the logs won't be complete. So it's recommended to create an extra job for generating and committing the generated microprints.

## Usage

```
name: Generate microprint of job

on: 
  push:

jobs:
  work_to_be_logged:
    runs-on: ubuntu-latest

    steps:
      {Your job steps}

  generate_microprint_of_first_job:
    runs-on: ubuntu-latest

    # If the job doesn't finish first, the logs won't be complete.
    needs: work_to_be_logged

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Get microprint of jobs logs
        uses: AlphaSteam/microprint-generator@v3
        with: # None of the inputs are required (though some are really recommended)

            # ====================================================================================
            # Github inputs

            # You can generate microprints of jobs on another repository if needed. By default it expects the job to be on the same repository.
            #
            # Default: ${{ github.repository }}
            
            repository: 

            # Job that's going to get used for microprint generation. By default it uses the job where the action is called. Not recommended as 
            # the logs don't get generated by the GitHub API until the job has finished all it's steps.
            #
            # Default: ${{ github.job }} (Not recommended!)
            
            job_name: work_to_be_logged

            # Personal access token (PAT) used to fetch the logs of the requested job. If the repo is public, it needs the public-repo scope,
            # if not, repo.
            # [Learn more about creating and using encrypted secrets](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/creating-and-using-encrypted-secrets)
            #
            # Default: ${{ github.token }}
            
            github_token: ${{ secrets.pat }}

            # Reference to the branch targeted
            #
            # Default: ${{ github.ref }} (Current branch)
            
            ref: ${{ github.ref }}

            # ====================================================================================
            # Log inputs

            # Whether or not to save the logs retrieved with the GitHub API as plain text
            #
            # Default: true 
            
            save_log: true

            # The name of the plain text logs file (Without the extension)
            #
            # Default: logs
            
            log_filename: custom_log_name

            # The directory where to save the plain text logs file. It saves it in the root of the repository by default.
            #
            # Default: ./
            
            log_path: ./Examples/With-custom-rules/

            # ====================================================================================
            # Microprint inputs

            # The name of the generated microprint (Without extension).
            #
            # Default: microprint
            
            microprint_filename: custom_microprint_name

            # The directory where to save the generated microprint. It saves it in the root of the repository by default.
            #
            # Default: ./
            
            microprint_path: ./Examples/With-custom-rules/

            # How to render the microprint. There's two options, 'svg' and 'raster'. The latter has some limitations.
            # Mainly low resolution and lack of custom fonts.
            #
            # Default: svg
            
            microprint_render_method: svg

            # The name for the config file (Without extension).
            #
            # Default: config
            
            microprint_config_filename: custom_config_name

            # The directory where the config.json file is located. This file is in charge of hosting the rules for generating the microprint.
            #
            # Default: ./
            
            microprint_config_path: ./Examples/With-custom-rules/

            # ====================================================================================
            # Microprint visualizer link inputs
            # NOTE: In private repositories, this will only work with generated personal access tokens. Not with the one generated by GitHub.

            # Whether or not to save a file with a generated link to the microprint visualizer
            #
            # Default: true 
            
            generate_microprint_visualizer_link: true

            # The name for the markdown file with the link (Without extension).
            #
            # Default: microprint_visualizer
            
            microprint_visualizer_link_filename: custom_microprint_visualizer

            # The directory where the markdown file with the generated link will be saved
            #
            # Default: ./
            
            microprint_visualizer_link_path: ./Examples/With-custom-rules/

            # ====================================================================================
            # Matrix inputs
            
            # Matrix values. Only change if you want to hardcode the matrix values. NOT RECOMMENDED.
            #
            # Default: ${{matrix && toJSON(matrix)}}

            matrix: ${{matrix && toJSON(matrix)}}


      # Here you can use any action for committing the generated files. But if you don't commit them, they'll be lost.

      - name: Commit microprint
        uses: EndBug/add-and-commit@v9
          with:
            message: Updated custom rules microprint
            pull: '--rebase --autostash'
      
```
## Microprint rules

There needs to be a set of rules to generate the microprints. These dictate what gets highlighted in the log and with what color. For that, there has to be a configuration JSON file in the repo. (By default in the root directory and with the name config.json).

The configuration file is optional and all the sections inside of it are optional too. (Without the configuration file, the microprint will be a render of the log without any highlight).

Here's an example with all the configurations that it can control (comments added for explanation purposes, not valid JSON):

For a valid example [click here](Examples/Mid-job/config.json)

```
{
  # Changes the scale of the font in the generated microprint.
  # Default: 1
  "scale": 2,

  # Changes the vertical spacing between each row.
  # Default: 1
  "vertical_spacing": 1.4,

  # Changes the width of the microprint (or each column if there's more than one)
  # Default: 120
  "microprint_width": 140,

  # Changes the max height of the microprint
  # If "number_of_columns" is set, this parameter is not used.
  # The microprint will be divided in columns to fulfill the desired height.
  # Default: Total log height. No limit
  "max_microprint_height": 300,

  # Changes the number of columns to render.
  # If this parameter is set, "max_microprint_height" is not used.
  # The height of the microprint will be set automatically to fulfill the desired number of columns
  # Default: Total log height. No limit
  "number_of_columns": 4,

  # Changes the size of the gap between columns
  # Default: 0.2
  "column_gap_size": 0.3,

  # Changes the color of the gap between columns
  # Default: "white"
  "column_gap_color": "red",

  # These define the default colors that are used in case no color was defined for
  # a certain rule. If this section is not present, both colors will be the
  # default ones.
  "default_colors": {
    # Default background color in case no background color is set
    # Default: white
    "background_color": "rgb(30, 30, 30)",

    # Default text color in case no background color is set
    # Default: black
    "text_color": "white"
  },

  # This section contains all the rules for the colors of the microprint
  # Each key corresponds to the word it needs to have in a row to use those
  # colors.
  
  # For example, if the key is "error" and the row contains the
  # word "error", then the whole row will be colored with the rules inside the
  # object

  # If any of the two colors is not set (text or background), the default ones 
  # are used.
  "line_rules": {
    "error": {
      "text_color": "red",
      "background_color": "white"
    },
    "installing": {
      "text_color": "white",
      "background_color": "green"
    },
    "command": {
      "text_color": "purple"
    },
    "warning": {
      "text_color": "black",
      "background_color": "yellow"
    },
    "fetching": {
      "text_color": "black",
      "background_color": "orange"
    },
    "complete": {
      "text_color": "green",
      "background_color": "white"
    }
  },
  
  # This section contains fonts to be embedded to the svg. If the fonts work
  # natively in the place where you want to see the svg, there's no need to
  # do this. (Only svg render)

  "additional_fonts": {

    # This sub-section contains fonts to be loaded from google fonts.

    # "name" is the name to assign the embedded font. This name is the one that
    # needs to be used when setting the font-family of the microprint.

    # "google_font_url" is the url from where to load the google font.

    # Both are required.
    "google_fonts": [
      {
        "name": "Anton",
        "google_font_url": "https://fonts.googleapis.com/css?family=Anton"
      },
      {
        "name": "Acme",
        "google_font_url": "https://fonts.googleapis.com/css?family=Acme"
      }
    ],

    # This sub-section contains fonts to be loaded from the repo, as a truetype
    # font file.

    # "name" is the name to assign the embedded font. This name is the one that
    # needs to be used when setting the font-family of the microprint

    # "truetype_file" is the path to the truetype font file. Includes the name of
    # the file with the extension.

    # Both are required.
    "truetype_fonts": [
      {
        "name": "NotoSans",
        "truetype_file": "./fonts/NotoSans-Regular.ttf"
      }
    ]
  },

  # This sets the font-family of the svg. If the first font is not available 
  # or cannot be loaded in the system, the next one is going to be used. 
  # (Only svg render)

  # Default: Sans
  "font-family": "Acme, Anton, NotoSans, Sans, Cursive"
}
```
