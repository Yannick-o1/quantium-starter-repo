#!/usr/bin/env bash

set -o nounset
set -o pipefail

project_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
virtual_environment="${project_directory}/.venv"
activation_script="${virtual_environment}/bin/activate"

if [[ ! -f "${activation_script}" ]]; then
    printf 'Error: virtual environment not found at %s\n' \
        "${virtual_environment}" >&2
    exit 1
fi

if ! source "${activation_script}"; then
    printf 'Error: could not activate the project virtual environment.\n' >&2
    exit 1
fi

if ! cd "${project_directory}"; then
    printf 'Error: could not enter the project directory.\n' >&2
    deactivate
    exit 1
fi

printf 'Running the Quantium visualiser test suite...\n'

if python -m pytest; then
    exit_code=0
    printf 'Test suite passed.\n'
else
    exit_code=1
    printf 'Test suite failed.\n' >&2
fi

deactivate
exit "${exit_code}"
