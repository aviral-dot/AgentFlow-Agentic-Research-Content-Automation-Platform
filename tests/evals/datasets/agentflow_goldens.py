from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Research NVIDIA and write a short 50-word blog "
                "about the research."
            )
        ),
    ]
)