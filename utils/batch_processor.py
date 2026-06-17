"""
Batch processor with configurable size and error isolation.
Processes items in chunks to avoid memory pressure and rate limits.
"""
from typing import TypeVar, Callable, Iterable, Iterator
import logging

T = TypeVar('T')
R = TypeVar('R')

logger = logging.getLogger(__name__)


def chunked(iterable: Iterable[T], size: int) -> Iterator[list[T]]:
    """Split an iterable into chunks of the given size."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def process_batch(
    items: list[T],
    fn: Callable[[T], R],
    batch_size: int = 100,
    skip_errors: bool = True,
) -> tuple[list[R], list[tuple[T, Exception]]]:
    """
    Process items in batches, collecting results and errors separately.

    Returns:
        (results, errors) where errors is a list of (item, exception) tuples.
    """
    results: list[R] = []
    errors: list[tuple[T, Exception]] = []

    for batch in chunked(items, batch_size):
        for item in batch:
            try:
                results.append(fn(item))
            except Exception as exc:
                if skip_errors:
                    logger.warning("Batch item failed: %s — %s", item, exc)
                    errors.append((item, exc))
                else:
                    raise
        logger.debug("Processed batch of %d items", len(batch))

    return results, errors
