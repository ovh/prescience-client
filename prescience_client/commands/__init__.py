import questionary
from typing import Callable


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
        answers = questionary.prompt(questions)
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
        answers = questionary.prompt(questions)
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
        answers = questionary.prompt([question])
        arg_value = answers.get(arg_name)
    return arg_value


def get_args_or_prompt_input(
        arg_name: str,
        args: dict,
        message: str,
        force_interactive: bool = False,
        validator=None,
        filter_func=None,
        default=None
):
    arg_value = args.get(arg_name)
    if arg_value is None or force_interactive:
        question = {
            'type': 'input',
            'name': arg_name,
            'message': message,
        }
        if validator is not None:
            question['validate'] = validator
        if filter_func is not None:
            question['filter'] = filter_func
        if default is not None:
            question['default'] = default
        answers = questionary.prompt([question])
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
        choices_function=lambda: [x.get_source_id() for x in prescience.sources(page=1).content]
    )


def prompt_for_dataset_id_if_needed(args: dict, prescience):
    return get_args_or_prompt_list(
        arg_name='id',
        args=args,
        message='Which dataset do you want to get ?',
        choices_function=lambda: [x.dataset_id() for x in prescience.datasets(page=1).content]
    )
