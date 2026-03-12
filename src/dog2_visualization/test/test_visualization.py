#!/usr/bin/env python3
"""
Basic tests for dog2_visualization package
"""

import pytest


def test_package_import():
    """Test that the package can be imported"""
    import dog2_visualization
    assert dog2_visualization.__version__ == '0.1.0'


def test_placeholder():
    """Placeholder test to ensure test framework works"""
    assert True


if __name__ == '__main__':
    pytest.main([__file__])
