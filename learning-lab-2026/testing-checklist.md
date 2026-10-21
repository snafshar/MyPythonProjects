# Python testing checklist

- Test typical inputs and boundary values.
- Verify invalid input raises a clear exception.
- Keep tests deterministic and independent of network access.
- Use temporary directories for filesystem tests.
- Run `python -m unittest discover -s learning-lab-2026 -v` from the repository root after adjusting import paths if needed.
- Include the exact Python version and command in bug reports.