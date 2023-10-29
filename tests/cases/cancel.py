import time

import inngest
import tests.helper

from . import base

_TEST_NAME = "cancel"


class _State(base.BaseState):
    is_done: bool = False


def create(
    client: inngest.Inngest,
    framework: str,
    is_sync: bool,
) -> base.Case:
    test_name = base.create_test_name(_TEST_NAME, is_sync)
    event_name = base.create_event_name(framework, test_name, is_sync)
    state = _State()

    @inngest.create_function_sync(
        cancel=[
            inngest.Cancel(
                event=f"{event_name}.cancel",
                if_exp="event.data.id == async.data.id",
            ),
        ],
        fn_id=test_name,
        trigger=inngest.TriggerEvent(event=event_name),
    )
    def fn_sync(
        *, run_id: str, step: inngest.StepSync, **_kwargs: object
    ) -> None:
        state.run_id = run_id

        # Wait a little bit to allow the cancel event to be sent.
        time.sleep(3)

        # The test will need to wait for this function's logic to finish even
        # though it's cancelled. Without this, Tornado will error due to logic
        # still running after the test is done.
        state.is_done = True

    @inngest.create_function(
        cancel=[
            inngest.Cancel(
                event=f"{event_name}.cancel",
                if_exp="event.data.id == async.data.id",
            ),
        ],
        fn_id=test_name,
        trigger=inngest.TriggerEvent(event=event_name),
    )
    async def fn_async(
        *, run_id: str, step: inngest.Step, **_kwargs: object
    ) -> None:
        state.run_id = run_id

        # Wait a little bit to allow the cancel event to be sent.
        time.sleep(3)

        # The test will need to wait for this function's logic to finish even
        # though it's cancelled. Without this, Tornado will error due to logic
        # still running after the test is done.
        state.is_done = True

    def run_test(_self: object) -> None:
        client.send_sync(inngest.Event(name=event_name, data={"id": "foo"}))
        run_id = state.wait_for_run_id()
        client.send_sync(
            inngest.Event(name=f"{event_name}.cancel", data={"id": "foo"})
        )
        tests.helper.client.wait_for_run_status(
            run_id,
            tests.helper.RunStatus.CANCELLED,
        )

        def assert_is_done() -> None:
            assert state.is_done

        base.wait_for(assert_is_done)

    if is_sync:
        fn = fn_sync
    else:
        fn = fn_async

    return base.Case(
        event_name=event_name,
        fn=fn,
        run_test=run_test,
        state=state,
        name=test_name,
    )
