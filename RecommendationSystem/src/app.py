from fastapi import FastAPI, Query
from .recommender import Recommender

app = FastAPI(title="Movie Recommendation System", version="1.1")

recommender = Recommender()

@app.get("/")
def home():
    return {"message": "OK", "try": ["/docs", "/search?q=toy", "/recommend/movie?movie=Toy%20Story"]}

@app.get("/search")
def search(q: str = Query(..., description="substring of a movie title"), k: int = 10):
    return {"results": recommender.search_titles(q, k)}

@app.get("/recommend/movie")
def recommend_movie(movie: str):
    recs = recommender.get_recommendations(movie)
    if not recs:
        return {"error": f"Movie not found for query: {movie}", "hint": "/search?q=toy"}
    return {"query": movie, "recommendations": recs}

@app.get("/recommend/user/{user_id}")
def recommend_user(user_id: int):
    try:
        recs = recommender.recommend_for_user(user_id)
        return {"user_id": user_id, "recommendations": recs}
    except KeyError:
        return {"error": f"User {user_id} not found"}