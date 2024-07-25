# test_common.py
import pytest
import os
from app.utils.common import setup_logging

def test_setup_logging(monkeypatch):
    """
    Test the setup_logging function to ensure it completes without error.
    """

    # Create a temporary directory and a dummy logging.conf file
    temp_dir = '/tmp/test_logging'
    os.makedirs(temp_dir, exist_ok=True)
    logging_conf_path = os.path.join(temp_dir, 'logging.conf')

    with open(logging_conf_path, 'w') as f:
        f.write("""
        [loggers]
        keys=root

        [handlers]
        keys=consoleHandler

        [formatters]
        keys=simpleFormatter

        [logger_root]
        level=DEBUG
        handlers=consoleHandler

        [handler_consoleHandler]
        class=StreamHandler
        level=DEBUG
        formatter=simpleFormatter
        args=(sys.stdout,)

        [formatter_simpleFormatter]
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
        """)

    # Monkeypatch the get_settings function to return the temporary directory
    def mock_get_settings():
        class MockSettings:
            LOGGING_CONFIG_PATH = logging_conf_path

        return MockSettings()

    monkeypatch.setattr('app.dependencies.get_settings', mock_get_settings)

    try:
        # Run the setup_logging function
        setup_logging()
    except Exception as e:
        pytest.fail(f"setup_logging raised an exception: {e}")

    # Cleanup
    os.remove(logging_conf_path)
    os.rmdir(temp_dir)

