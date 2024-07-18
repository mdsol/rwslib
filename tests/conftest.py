import pytest
import os


@pytest.fixture(scope="class")
def car_message(request):
    with open(
            os.path.join(
                os.path.dirname(__file__), "fixtures", "car_message.xml"
            ), 'r'
    ) as fh:
        content = fh.read()
    request.cls.car_message = content


@pytest.fixture(scope="class")
def double_byte_chars(request):
    with open(os.path.join(
            os.path.dirname(__file__), "fixtures", "test_double_byte_chars.xml"), "r+b") as fh:
        content = fh.read()
    request.cls.double_byte_chars = content
