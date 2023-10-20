import datetime

import inngest


@inngest.create_function(
    inngest.FunctionOpts(id="two-steps-and-sleep", name="Two steps and sleep", retries=0),
    inngest.TriggerEvent(event="app/two-steps-and-sleep"),
)
def fn(*, step: inngest.Step, **_: object) -> str:
    def _get_user_id() -> int:
        return 1

    user_id = step.run("get-user-id", _get_user_id)

    def _print_user_id() -> str:
        return f"user ID is {user_id}"

    step.run("print-user-id", _print_user_id)

    step.sleep_until(
        "zzzzz",
        (datetime.datetime.now() + datetime.timedelta(seconds=3)),
    )

    return "done"
