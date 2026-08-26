from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Research NVIDIA and write a short 50-word blog "
                "about the research."
            )
        ),
        Golden(
            input=(
                "Research NVIDIA and write a short blog about the "
                "research, then prepare it for email delivery."
            )
        ),
        Golden(
            input=(
                "Research NVIDIA and create a concise technical blog "
                "about the research."
            )
        ),
    ]
)