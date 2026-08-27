from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Research NVIDIA and write a short blog about the "
                "research, then prepare it for email delivery"
            )
        ),
        
    ]
)