from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[

        # ====================================================
        # INDEPENDENT BLOG
        # ====================================================

        Golden(
            input=(
                "Write a concise professional blog about the "
                "benefits of cloud computing for modern businesses."
            ),
        ),

        Golden(
            input=(
                "Write a professional blog explaining how remote "
                "work is changing the future of the workplace."
            ),
        ),

        Golden(
            input=(
                "Write a concise professional blog about the "
                "importance of cybersecurity for modern businesses."
            ),
        ),

        Golden(
            input=(
                "Write a professional blog about how data analytics "
                "is helping businesses make better decisions."
            ),
        ),
    ]
)