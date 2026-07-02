from __future__ import annotations

import pytest

from contextos.evaluation.run import load_dataset, run_evaluation


@pytest.mark.asyncio
async def test_local_evaluation_dataset_passes_with_fake_providers() -> None:
    results = await run_evaluation(load_dataset())

    assert results
    assert all(result.passed for result in results), [
        f"{result.name}: {result.detail}" for result in results if not result.passed
    ]
