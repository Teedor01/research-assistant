class ResearchTimeoutError(Exception):
    """Raised when the graph run exceeds the hard wall-clock backstop —
    should be rare, since identify_gaps enforces its own time budget
    internally; this is a last-resort safety net, not the primary control."""
    pass


class ResearchFailedError(Exception):
    """Raised for any unexpected failure during a graph run that we want
    to surface as a clean, user-safe error rather than a raw traceback."""
    pass