import httpx
async def get_movie_extra_data(imdb_id: str):
        url = "https://movie-database-alternative.p.rapidapi.com/"
        querystring = {"r":"json","i":imdb_id}
        headers = {
            "X-RapidAPI-Key": "54a0803868msh446ebfe6adda6f5p1ab66djsn0d1863f22e5e",
            "X-RapidAPI-Host": "movie-database-alternative.p.rapidapi.com"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=querystring)
        data = response.json()
        if data["Response"] == "True":
            extra_data = {
                "imdbRating": float(data["imdbRating"]),
                "imdbVotes": int(data["imdbVotes"].replace(',', '')),
                "Language": data["Language"],
                "Country": data["Country"]
            }
            return extra_data
        else:
            return "No results found."


    