from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Write a professional email to "
                "rrrttzch@gmail.com requesting a meeting "
                "to discuss the project progress."
            )
        ),
        Golden(
            input=(
                "Send a concise professional email to "
                "rrrttzch@gmail.com thanking them for "
                "their support on the project."
            )
        ),
        Golden(
            input=(
                "Write a professional email to "
                "rrrttzch@gmail.com informing them that "
                "the project report has been completed."
            )
        ),
    ]
)