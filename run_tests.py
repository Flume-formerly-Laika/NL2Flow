#!/usr/bin/env python3
"""
Test runner script for NL2Flow.
This script runs tests with proper configuration and handles warnings.
"""

import subprocess
import sys
import os

def run_tests():
    """Run pytest with proper configuration."""
    # Set environment variables to suppress warnings
    env = os.environ.copy()
    env['PYTHONWARNINGS'] = 'ignore::DeprecationWarning:botocore.*,ignore::DeprecationWarning:httpx.*'
    
    # Run pytest with proper arguments
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--strict-markers',
        '--strict-config'
    ]
    
    try:
        result = subprocess.run(cmd, env=env, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 