from behave import fixture
from firenado import launcher


@fixture
def firenado_app(context, timeout=30, **kwargs):

    context.launcher = launcher.FirenadoLauncher()
    print(context.launcher)
    yield context.launcher
