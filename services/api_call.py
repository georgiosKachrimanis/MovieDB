import asyncio
from movie_service import MovieService


async def main():
    result: float = await MovieService.get_movie_extra_data("tt4154796")
    print(result)


asyncio.run(main())
