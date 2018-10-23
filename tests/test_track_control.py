import asyncio
from utils import wait_for_event
import pytest


@pytest.mark.asyncio
async def test_wait_for_barrier_event(track_control):
    wait_for_task = asyncio.create_task(wait_for_event(track_control.barrier_event))
    assert not wait_for_task.done()
    await track_control._trigger_barrier()
    await wait_for_task


def test_power_on(track_control):
    track_control.power_on()
    assert track_control.track_power_serial.is_high


def test_power_off(track_control):
    track_control.power_off()
    assert not track_control.track_power_serial.is_high

