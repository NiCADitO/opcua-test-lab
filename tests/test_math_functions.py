import pytest
from src import server_methods


def test_add():
    result = server_methods.add.__wrapped__(None, 2, 2)
    assert result == 4

    #shorthand assert
    assert server_methods.add.__wrapped__(None, 2, 2) != 5

def test_sub():
    assert server_methods.subtract.__wrapped__(None, 2, 2) == 0

    assert server_methods.subtract.__wrapped__(None, 2, 2) != 1 

def test_mult():
    assert server_methods.multiply.__wrapped__(None, 3, 1) == 3

    assert server_methods.multiply.__wrapped__(None, 4, 4) == 16

# test helper function
def test_helper_div():
    assert server_methods.divide_numbers(4, 2) == 2.0

def test_div():
    assert server_methods.divide.__wrapped__(None, 4, 2) == 2.0

def test_div_by_zero():
    with pytest.raises(ValueError, match="cannot divide by zero"):
        server_methods.divide_numbers(5, 0)

def test_is_even():
    assert server_methods.is_even.__wrapped__(None, 2) is True

    assert server_methods.is_even.__wrapped__(None, 1) is False