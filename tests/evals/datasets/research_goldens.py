from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Research the benefits of cloud computing for "
                "modern businesses. Provide concise factual "
                "findings."
            )
        ),
        Golden(
            input=(
                "Research the importance of cybersecurity for "
                "modern businesses. Provide concise factual "
                "findings."
            )
        ),
        Golden(
            input=(
                "Research how artificial intelligence is being "
                "used by businesses to improve productivity. "
                "Provide concise factual findings."
            )
        ),
    ]
)