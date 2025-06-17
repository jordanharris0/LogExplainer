import os  # allows access to env variables
from dotenv import load_dotenv  # allows access to .env file
from openai import OpenAI  # allows access to OpenAI API

import time  # allows access to time function
import json  # allows access to JSON functions
import csv  # allows access to CSV functions


# load API key from .env file
load_dotenv()  # reads .env file and temporarily adds those values to env variables

# configures OpenAI client to use the API key when making requests and assigns it to the openai.api_key variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# gets user input in the console and stores it in the variable log_input

# prompted to provide a file or a single log message
use_file = input('Do you wish to provide a log file? (y/n): ').strip().lower()

log_lines = []

# if yes reads file from the file system
if use_file == 'y':
    # keeps prompting user until a valid file is provided
    while not log_lines:
        file_path = input('Enter the path to the log file: ').strip()

        print(f'Reading File {file_path}...')
        time.sleep(1)  # adds short delay for bette user experince

        try:
            with open(file_path, 'r') as file:
                # removes empty lines and white spaces
                log_lines = [line.strip() for line in file if line.strip()]

                print('Generating prompt...')
                time.sleep(0.5)

        except FileNotFoundError:
            print(f'File not found: {file_path}. Please try again.')

# prompts user to provide a single log
else:
    log_input = input('Enter the log message you want to explain:\n')

    print(f'Reading input...')
    time.sleep(0.5)  # adds short delay for bette user experince

    log_lines = [log_input]

    print('Generating prompt...')
    time.sleep(0.5)

# ask user if they would like to export the explanation to a file
export = input(
    'Would you like to export the explanations to a file? (y/n): ').strip().lower()

output_path = None  # initialize output_path variable

if export == 'y':

    while not output_path:

        # get file name from user
        output_path = input(
            'Enter the output filename ending in .txt, .md, .json, .csv (e.g., explained_logs.md): ').strip()

        print(f'Preparing to save explanations to {output_path}...')
        time.sleep(1)

        # validation
        if not output_path.endswith(('.txt', '.md', '.json', '.csv')):
            print('Unsupported file format. Please use .txt, .md, or .json.')
            output_path = None  # resets output_path to prompt again

    if output_path.endswith('.json'):
        json_data = []
    elif output_path.endswith('.csv'):
        csv_data = []
    else:
        explanations = []  # initialize empty list to store explanations
else:
    output_path = None

# loops through each line in log_lines and sends it to OpenAI API for explanation
for i, log in enumerate(log_lines):

    # send request to OpenAI API to explain the log message
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',  # specifies the model to use

        # full prompt that gets sent to the model
        messages=[
            {
                # assigns role of GPT model
                'role': 'system', 'content': 'You are a helpful assistant that explains log messages in detail.'
            },
            {
                # user input is passed to the model
                'role': 'user', 'content': f'Explain this log:\n{log}'
            },
        ],
        # keeps putput more predictable and concise (lower = more focused, higher = more creative)
        temperature=0.3
    )

    # response = full JSON returned by the OpenAI API
    # .choices[0].message.content grabs actual text response from GPT model
    explanation = response.choices[0].message.content

    if output_path:
        # if output_path is provided, append the explanation to json list
        if output_path.endswith('.json'):
            json_data.append({
                "line": i + 1,
                "log": log,
                "explanation": explanation
            })
            print(f'Appending explanation for line {i + 1}...')
            time.sleep(0.5)

        # elif append the explanation to csv list
        elif output_path.endswith('.csv'):
            csv_data.append([log, explanation])
            print(f'Appending explanation for line {i + 1}...')
            time.sleep(0.5)

        # else append the explanation list
        else:
            explanations.append(
                f'## Explanation for Line {i + 1}:\n{log}\n\n{explanation}\n\n')
            print(f'Appending explanation for line {i + 1}...')
            time.sleep(0.5)
    else:

        # prints the log message being explained
        print(f'\nExplaining line {i + 1}: \n{log}...')

        # prints the explanation to the console
        print(f'\nExplanation:\n\n{explanation}')

# write the explanation to the file
if output_path:

    # if json file, write the json_data to the file
    if output_path.endswith('.json'):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
            print(f'\n✅ Explanations saved to {output_path}.')

    # elif csv file, write the csv_data to the file
    elif output_path.endswith('.csv'):
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Log Line', 'Explanation'])
            for line, explanation in csv_data:
                writer.writerow([line.strip(), explanation.strip()])
            print(f'\n✅ Explanations saved to {output_path}.')

    # else if txt or md file, write the explanations to the file
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(explanations))

            print(f'\n✅ Explanations saved to {output_path}.')
