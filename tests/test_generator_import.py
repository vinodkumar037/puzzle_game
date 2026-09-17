import importlib


def test_generator_exports_generate_level():
    module = importlib.import_module("app.generator")
    assert hasattr(module, "generate_level")
    assert callable(module.generate_level)
