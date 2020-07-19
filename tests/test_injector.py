from typing import Generic, TypeVar

from rinject import Injector, FactoryProvider, InstanceProvider, ValueProvider


class OtherClass:
    pass


class SomeClass:
    pass


class AnotherClass:
    def __init__(self, other_class: OtherClass):
        self.other_class = other_class


class ValueMock:
    def __init__(self, by_value: str):
        self.by_value = by_value


class ClassInstanceMock:
    def __init__(self, some_class: SomeClass):
        self.some_class = some_class


class AnotherInstanceMock:
    def __init__(self, another_class: AnotherClass):
        self.another_class = another_class


T = TypeVar("T")


class C:
    pass


class A(Generic[T]):
    thing: T


class B(A[C]):
    thing = C

    def __init__(self, c: C):
        self.c = c


def test_inject_via_value_provider():
    i = Injector(logger=print)
    i.register(key="by_value", provider=ValueProvider(value="a value"))
    vm = i.inject(ValueMock)
    assert "a value" == vm.by_value


def test_inject_via_instance_provider():
    i = Injector(logger=print)
    i.register(key=SomeClass, provider=InstanceProvider(SomeClass))
    im = i.inject(ClassInstanceMock)
    assert isinstance(im.some_class, SomeClass)


def test_instance_provider_injects_same_instance_each_time():
    i = Injector(logger=print)
    i.register(key=SomeClass, provider=InstanceProvider(SomeClass))
    im1 = i.inject(ClassInstanceMock)
    im2 = i.inject(ClassInstanceMock)
    assert isinstance(im1.some_class, SomeClass)
    assert isinstance(im2.some_class, SomeClass)
    assert im1.some_class is im2.some_class


def test_inject_via_factory_provider():
    i = Injector(logger=print)
    i.register(key=SomeClass, provider=FactoryProvider(SomeClass))
    im = i.inject(ClassInstanceMock)
    assert isinstance(im.some_class, SomeClass)


def test_factory_provider_injects_different_instance_each_time():
    i = Injector(logger=print)
    i.register(key=SomeClass, provider=FactoryProvider(SomeClass))
    im1 = i.inject(ClassInstanceMock)
    im2 = i.inject(ClassInstanceMock)
    assert isinstance(im1.some_class, SomeClass)
    assert isinstance(im2.some_class, SomeClass)
    assert im1.some_class is not im2.some_class


def test_injector_recursively_injects():
    i = Injector(logger=print)
    i.register(key=AnotherClass, provider=InstanceProvider(AnotherClass))
    i.register(key=OtherClass, provider=InstanceProvider(OtherClass))
    im = i.inject(AnotherInstanceMock)
    assert isinstance(im.another_class, AnotherClass)
    assert isinstance(im.another_class.other_class, OtherClass)


def test_inject_where_generics_in_base_class():
    """
    Regression test where there is a Generic in a base class, doing inspect.sig does not return the real signature
    """
    i = Injector(logger=print)
    i.register_instance(C, C)
    i.register_instance(B, B)
    im = i.resolve(B)
    assert isinstance(im, B)
