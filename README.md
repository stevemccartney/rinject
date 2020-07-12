# rInject

A flexible (annotations or keys) but simple dependency injection library for Python 3.


## Installation

```pip install rinject```


## Usage

```python
from rinject import Injector
from datetime import datetime


injector = Injector()


class A:
    def __init__(self, greeting: str):
        self.greeting = greeting

    def __call__(self, name: str):
        print(f"{self.greeting} {name}")


class B:
    def __init__(self, a: A, name: str):
        self.a = a
        self.name = name

    def __call__(self):
        self.a(self.name)


if __name__ == "__main__":
    injector.register_value("greeting", "Hello")
    injector.register_instance(A, A)
    injector.register_instance(B, B)
    injector.register_factory("name", lambda: "Steve@" + datetime.utcnow().isoformat())

    b = injector.resolve(B)
    b()  # outputs => Hello Steve

    b2 = injector.resolve(B)
    assert b is b2
```

