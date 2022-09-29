import asyncio
import enum
import logging
import sys
from dataclasses import dataclass


class State(enum.Enum):
    IDLE = enum.auto()  # 空闲状态
    STARTED = enum.auto()  # 开始状态
    PAUSED = enum.auto()  # 暂停状态


@dataclass(frozen=True)
class Event:
    name: str


START = Event('Start')
PAUSE = Event('Pause')
STOP = Event('Stop')
EXIT = Event('Exit')

STATES = (START, PAUSE, STOP, EXIT)
CHOICE = '\n'.join([f'{i}: {state.name}' for i, state in enumerate(STATES)])

MENU = f'''
Menu
Enter you choice:
{CHOICE}
'''

# 定义 从状态1切换到状态2可能发生的所有情况
TRANSITIONS = {
    (State.IDLE, START): State.STARTED, # 从空闲切换到开始
    (State.IDLE, PAUSE): State.IDLE,
    (State.IDLE, STOP): State.IDLE,

    (State.STARTED, START): State.STARTED, # 从开始切换到开始
    (State.STARTED, PAUSE): State.PAUSED,
    (State.STARTED, STOP): State.IDLE,

    (State.PAUSED, START): State.STARTED,
    (State.PAUSED, PAUSE): State.PAUSED,
    (State.PAUSED, STOP): State.IDLE,

    (State.IDLE, EXIT): State.IDLE,
    (State.STARTED, EXIT): State.IDLE,
    (State.PAUSED, EXIT): State.IDLE,
}


class StateMachineException(Exception):
    pass


class StartStateMachineException(StateMachineException):
    pass


# 用户出入Stop引发的异常
class StopStateMachineException(StateMachineException):
    pass


async def next_state(state_machine, event, *, exc=StateMachineException):
    '''定义从一个状态往另一个状态过渡'''
    try:
        if state_machine:
            # state_machine 是个异步生成器
            await state_machine.asend(event)
    except StopAsyncIteration: # 在生成器上调用aclose时，会抛出
        if exc != StopStateMachineException:
            raise exc()
    except Exception:
        raise exc()


async def start_statemachine(state_machine):
    # 向状态机传递event, 此时如果生成器被close 会报StartStateMachineException 异常
    await next_state(state_machine, None, exc=StartStateMachineException)


async def stop_statemachine(state_machine):
    # 向状态机传递EXIT event， 此时如果生成器被close会报StopStateMachineException
    await next_state(state_machine, EXIT, exc=StopStateMachineException)


async def create_state_machine(transitions, *, logger=None):
    '''返回一个异步生成器，它可以根据Event转化状态'''
    if not logger:
        logger = logging.getLogger(__name__)
    event, current_state = None, State.IDLE  # 当前状态为空闲
    while event != EXIT:
        event = yield  # 传递事件
        edge = (current_state, event)
        if edge not in transitions:
            # 查看这种状态转换是否被定义
            logger.error('Cannot consume %s in state %s', event.name, current_state.name)

        next_state_ = transitions.get(edge) # 获取新状态
        logger.debug('Transitioning from %s to %s', current_state.name, next_state_.name)
        current_state = next_state_


def pick_next_event(logger):
    '''让用户键入一个状态'''
    next_state_ = None
    while not next_state_:
        try:
            next_state_ = STATES[int(input(MENU))]
        except (ValueError, IndexError):
            logger.error('Invalid choice')
            continue
    return next_state_


async def main(logger):
    state_machine = create_state_machine(TRANSITIONS, logger=logger)
    try:
        await start_statemachine(state_machine)  # 激活生成器

        while True:
            event = pick_next_event(logger)
            if event != EXIT:
                await next_state(state_machine, event)
            else:
                await stop_statemachine(state_machine)

    except StartStateMachineException:
        logger.error('Cannot start state machine')
    except StopStateMachineException:
        logger.error('Cannot stop state machine')
    except StateMachineException:
        logger.error('Transitioning the statemachine was unsuccessful')


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

try:
    asyncio.get_event_loop().run_until_complete(main(logger))
except KeyboardInterrupt:
    logger.info('closing event loop')





