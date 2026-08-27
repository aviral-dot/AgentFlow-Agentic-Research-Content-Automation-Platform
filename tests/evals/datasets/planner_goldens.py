# mypy: ignore-errors

from deepeval.dataset import EvaluationDataset, Golden


dataset = EvaluationDataset(
    goldens=[
      
        Golden(
            input=(
                          "Research NVIDIA's latest AI developments, "
                                          "write a blog about them, and email the blog "
                                          "to rrrttzch@gmail.com."
                        )
            
        ),

    
        Golden(
            input=(
                "Research the benefits of cloud computing "
                "and write a blog about it."
            )
        ),

       

        Golden(
            input="Write a blog about the benefits of artificial intelligence."
        ),

     
        Golden(
            input=(
                "Send an email to rrrttzch@gmail.com "
                "reminding them about tomorrow's meeting."
            )
        ),

       

        Golden(
            input=(
                "Research NVIDIA's latest AI developments, "
                "write a blog about them, and email the blog "
                "to rrrttzch@gmail.com."
            )
        ),
    ]
)