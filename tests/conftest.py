def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'slow: exhaustive check against all Yellow replies')
