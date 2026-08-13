import json
from pathlib import Path


STATE_FILE = Path("data/state/pipeline_state.json")


def save_state(state):
    """
    Save the current pipeline state to disk.

    Creates the parent directory and state file if
    they do not already exist.
    """

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=2,
        )


def load_state():
    """
    Load the previously saved pipeline state.

    Returns:
        The saved state dictionary, or None if the
        state file does not exist.
    """

    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def is_previous_run_successful():
    """
    Check whether the most recent pipeline run
    completed successfully.
    """

    state = load_state()

    if state is None:
        return False

    return state.get("last_status") == "SUCCESS"


def main():
    """
    Simple state module entry point.
    """

    state = load_state()

    if state is None:
        print("No previous pipeline state found.")
        return

    print("Previous pipeline state:")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()

