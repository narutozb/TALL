## 什么是装饰器（Decorator）？
在 Python 中，装饰器是一种用于“增强”或修改函数或类的行为而无需更改其源代码的特殊函数或类。
简单来说，装饰器接收一个函数或类作为输入，并返回一个被“包装”后的函数或类，
从而在调用被装饰对象时实现一些额外的功能。


## 装饰器的基本原理

装饰器本质是高阶函数（Higher-order Function），满足两个条件之一即为高阶函数：

* 接受一个或多个函数作为输入参数。
* 返回一个函数作为结果。


典型的装饰器写法如下：

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        # 在函数执行前，可以执行一些操作
        result = func(*args, **kwargs)
        # 在函数执行后，也可以执行一些操作
        return result
    return wrapper

# 然后使用 @decorator 的语法糖来装饰目标函数：
@decorator
def my_function():
    print("Original function is running...")
```

当执行 my_function() 时，其实执行的是 wrapper() 内部逻辑，即 my_function 被“包装”在 wrapper 里。


## 为什么要使用装饰器？

* 代码复用：将通用的逻辑（如日志记录、性能测量、权限检查、事务管理、缓存控制等）独立封装成装饰器，然后在需要的地方通过简单的 @装饰器名 进行复用。
* 分离关注点：业务逻辑不必被重复的样板代码（例如鉴权、计时）污染，使代码更加干净易读。
* 松耦合：装饰器可以轻松地添加或移除功能，而无需更改函数本身。

## 基本使用示例

打印函数运行时间的装饰器

```python
import time

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start:.4f} seconds")
        return result
    return wrapper

@timeit
def test_func(n):
    total = 0
    for i in range(n):
        total += i
    return total

print(test_func(1000000))
```






