from fastapi import APIRouter

router = APIRouter()


@router.get("/faqs")
def faqs():
    return [
        "What is the earliest accident year in the complete dataset?",
        "How many accidents involving personal injury occurred in Saxony in 2023?",
        "From which year onwards is data available for North Rhine-Westphalia?",
        "From which year onwards is data available for Mecklenburg-Western Pomerania?",
        "How many pedestrian accidents occurred in Berlin in 2023?",
        "What are the top 5 districts with the highest number of fatal accidents in 2024?",
        "How many bicycle accidents occurred in Dresden in 2024?",
        "Which municipalities in Saxony recorded zero accidents in 2023?"
    ]