import os
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException


async def get_movie_extra_data(imdb_id: str):
    print('inside aseync func')
    load_dotenv()
    url = "https://movie-database-alternative.p.rapidapi.com/"
    querystring = {"r": "json", "i": imdb_id}
    headers = {
        "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com",
    }
    print('after creating headers')
    async with httpx.AsyncClient() as client:
        print('waiting for response')
        response = await client.get(
            url,
            headers=headers,
            params=querystring,
        )
    data = response.json()
    print(f"the data are {data}")
    if data["Response"] == "True":
        extra_data = {
            "imdbRating": float(data["imdbRating"]),
            "imdbVotes": int(data["imdbVotes"].replace(",", "")),
            "Language": data["Language"],
            "Country": data["Country"],
        }
        return extra_data
    else:
        raise HTTPException(
            status_code=400,
            detail="Information was not available in www.movie_database",
        )
