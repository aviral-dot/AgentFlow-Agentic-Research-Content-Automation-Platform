from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Create a professional email to the team "
                "announcing that the AI project has been completed."
            )
        ),
        Golden(
            input=(
                "Write an email to my manager giving a concise "
                "update about the AI project."
            )
        ),
        Golden(
            input=(
                "Create an email announcing the new AI blog "
                "to the development team."
            )
        ),
        Golden(
            input=(
                "Write a professional email asking the team "
                "to attend tomorrow's meeting."
            )
        ),
        Golden(
            input=(
                "Create a concise project status update email."
            )
        ),
    ]
)