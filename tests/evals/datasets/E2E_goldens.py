from deepeval.dataset import EvaluationDataset
from deepeval.dataset.golden import Golden


dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "Research NVIDIA and write a short blog "
                "about the research."
            ),
            expected_output=(
                "A concise research-based blog about NVIDIA, "
                "covering its technology and recent developments."
            ),
        )
    ]
)