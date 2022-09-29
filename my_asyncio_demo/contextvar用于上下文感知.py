from contextvars import ContextVar
import contextvars
import functools

context = contextvars.copy_context()  # 当前上下文对象的一个浅拷贝
context_var = ContextVar('key', default=None)


def resetter(context_var_: ContextVar, token, invalid_values):
    value = context_var_.get()
    if value in invalid_values:
        context_var_.reset(token)


def blacklist(context_var_: ContextVar, value, resetter):
    old_value = context_var_.get()
    token = context_var_.set(value)
    # print('token: ', token)
    resetter(context_var_, token)
    print('old_value: ', old_value)


# 在Context上下文中，不断改变context_var，遇到黑名单时，利用token回退值
for i in range(10):
    context.run(blacklist, context_var, i, functools.partial(resetter, invalid_values=[5, 6, 7, 8, 9]))