import pytest
from track_control import BarrierEventTaskFactory, BarrierLoopTaskRunner, BarrierState, PowerState
from utils import context_switch
import asyncio


@pytest.fixture
async def barrier_loop_task_runner(track_control, arduino_track_control):
    barrier_ltr = BarrierLoopTaskRunner(track_control)
    barrier_ltr.start()
    assert barrier_ltr.is_running()
    yield barrier_ltr
    barrier_ltr.stop()


@pytest.mark.asyncio
async def test_barrier_event_task(track_control):
    barrier_etf = BarrierEventTaskFactory(track_control)
    task = barrier_etf.create_await_event_task()

    await context_switch()

    assert len(track_control._barrier_events) == 1
    assert not task.done()
    track_control.trigger_barrier()

    await context_switch()

    assert len(track_control._barrier_events) == 0
    assert task.done()
    await task


@pytest.mark.asyncio
async def test_barrier_loop(barrier_loop_task_runner, arduino_track_control, track_control):
    event = asyncio.Event()

    track_control.register_barrier_event(event)

    await context_switch()
    assert not event.is_set()

    arduino_track_control.mock_set_barrier_trigger()
    await context_switch()

    await event.wait()
    assert event.is_set()


def test_power_on(track_control):
    track_control.power_on()
    assert track_control.is_powered


def test_power_off(track_control):
    track_control.power_off()
    assert not track_control.is_powered
