import os

from typing import Callable
from PyInquirer import prompt

from prescience_client.utils.monad import Option


def get_args_or_prompt_list(
        arg_name: str,
        args: dict,
        message: str,
        choices_function: Callable,
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        questions = [
            {
                'type': 'list',
                'name': arg_name,
                'message': message,
                'choices': choices_function()
            }
        ]
        answers = prompt(questions)
        arg_value = answers.get(arg_name)
    return arg_value

def get_args_or_prompt_checkbox(
        arg_name: str,
        args: dict,
        message: str,
        choices_function: Callable,
        selected_function: Callable = lambda: [],
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        selected = selected_function()
        questions = [
            {
                'type': 'checkbox',
                'name': arg_name,
                'message': message,
                'choices': [{'name': x, 'checked': x in selected} for x in choices_function()]
            }
        ]
        answers = prompt(questions)
        arg_value = answers.get(arg_name)
    return arg_value

def get_args_or_prompt_confirm(
        arg_name: str,
        args: dict,
        message: str,
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        question = {
            'type': 'confirm',
            'name': arg_name,
            'message': message,
        }
        if arg_value is True or arg_value is False:
            question['default'] = arg_value
        answers = prompt([question])
        arg_value = answers.get(arg_name)
    return arg_value

def get_args_or_prompt_input(
        arg_name: str,
        args: dict,
        message: str,
        force_interactive: bool = False
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        questions = [
            {
                'type': 'input',
                'name': arg_name,
                'message': message,
            }
        ]
        answers = prompt(questions)
        arg_value = answers.get(arg_name)
    return arg_value

def prompt_for_model_id_if_needed(args: dict, prescience):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which model do you want to get ?',
        choices_function=lambda: [x.model_id() for x in prescience.models(page=1).content]
    )

def prompt_for_source_id_if_needed(args: dict, prescience):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which source do you want to get ?',
        choices_function=lambda: [x.source_id for x in prescience.sources(page=1).content]
    )

def prompt_for_dataset_id_if_needed(args: dict, prescience):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which dataset do you want to get ?',
        choices_function=lambda: [x.dataset_id() for x in prescience.datasets(page=1).content]
    )

def get_default_json_ouput():
    cwd = os.getcwd()
    full_output = os.path.join(cwd, 'output.json')
    return full_output