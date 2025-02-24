import functools

import maya.cmds as cmds


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ScriptJobManagerBase(metaclass=SingletonMeta):
    executed_job_list = []
    condition_and_event_parameters = [
        'attributeAdded',
        'attributeChange',
        'attributeDeleted',
        'conditionChange',
        'conditionFalse',
        'conditionTrue',
        'connectionChange',
        'event',
        'nodeDeleted',
        'nodeNameChanged',
        'optionVarChanged',
        'uiDeleted',
    ]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.registration_script_job_list = []  # 为每个子类初始化独立列表

    @classmethod
    def add_job(cls, **kwargs):
        if kwargs not in cls.registration_script_job_list:
            cls.registration_script_job_list.append(kwargs)

    @classmethod
    def run_jobs(cls):
        print(f'{cls.__name__}:运行ScriptJobs')
        for i in cls.registration_script_job_list:
            cls.executed_job_list.append(cmds.scriptJob(**i))

    @classmethod
    def kill_jobs(cls):
        for idx, i in enumerate(cls.executed_job_list):
            print(f'{cls.__name__}:删除已执行ScriptJobsID:{i}')
            cmds.scriptJob(kill=i)
            cls.executed_job_list.pop(idx)

        print(f'{cls.__name__}:清除ScriptJobs列表')
        cls.registration_script_job_list.clear()

    @classmethod
    def add_script_job_decorator(cls, *decorator_args, **decorator_kwargs):
        def decorator(func):
            # 如果方法是绑定方法，则保存原始函数（未绑定的函数对象）
            original = getattr(func, '__original_func__', None)
            if original is None:
                # 如果 func 有 __func__ 属性，则它是方法描述符
                original = getattr(func, '__func__', func)
                func.__original_func__ = original

            # 在函数定义时注册（只注册一次）
            for condition, lst in decorator_kwargs.items():
                if condition in cls.condition_and_event_parameters:
                    # 这里注册的是原始的 unbound 方法
                    lst.append(original)
            cls.registration_script_job_list.append(decorator_kwargs)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            wrapper.__original_func__ = original
            return wrapper

        return decorator


class ToolManager(ScriptJobManagerBase):
    tool_name: str = 'Tool Name'
    description: str = 'Description...'

    def __init__(self):
        pass
