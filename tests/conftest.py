import pytest
import random
import logging
# Configure info for all other tests.
# Run tests using:
# seba
# pytest tests
# (for more information:)
# pytest tests -s --log-cli-level=INFO

@pytest.fixture()
def app(request):
    # If test fails due to a 'random' value, we can repeat by passing
    # --seed
    logger = logging.getLogger("HotMech")
    logger.setLevel(logging.DEBUG)

    if request.config.option.seed is None:
        seed = random.randint(0, 1000)
        random.seed(seed)
        logger.info(f"Choosing random seed '{seed}'")
    else:
        seed = request.config.option.seed
        random.seed(seed)
        logger.info(f"Using passed seed '{seed}'")

    # Other setup can go here

    yield app

    # clean up / reset resources here

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def pytest_addoption(parser):
    # Want to be able to set the same seed to reproduce 'random' errors
    parser.addoption("--seed", action="store", default=None)
