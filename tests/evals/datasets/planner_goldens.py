from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input="Write a blog about LangGraph."
        ),
        Golden(
            input="Email Rahul telling him to attend school early."
        ),
        Golden(
            input="Research NVIDIA and write a blog about it."
        ),
        Golden(
            input=(
                "Generate a blog about AI agents and "
                "email the blog to Rahul."
            )
        ),
        Golden(
            input=(
                "Research NVIDIA, write a blog based on "
                "the research, and email the generated "
                "blog to Rahul."
            )
        ),
        Golden(
            input=(
                "Research NVIDIA and email Rahul telling "
                "him to attend school early."
            )
        ),
        Golden(
            input=(
                "Research NVIDIA and write a blog about it "
                "while emailing Rahul separately."
            )
        ),
    ]
)