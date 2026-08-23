from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input="Write a blog about retrieval augmented generation."
        ),
        Golden(
            input="Write a blog about multi-agent AI systems."
        ),
        Golden(
            input="Write an article about LangGraph."
        ),
        Golden(
            input="Create an email announcing the new AI project."
        ),
        Golden(
            input="Write a professional email about the project update."
        ),
        Golden(
            input="Create an email informing the team about tomorrow's meeting."
        ),
    ]
)