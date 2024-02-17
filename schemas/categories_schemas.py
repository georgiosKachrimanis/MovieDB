from enum import Enum
from pydantic import BaseModel


class CategoryBase(BaseModel):
    category_name: str


class Category(CategoryBase):
    id: int


class CategoryMenu(str, Enum):
    action = "Action"
    adventure = "Adventure"
    animation = "Animation"
    biography = "Biography"
    comedy = "Comedy"
    crime = "Crime"
    documentary = "Documentary"
    drama = "Drama"
    family = "Family"
    fantasy = "Fantasy"
    film_noir = "Film Noir"
    history = "History"
    horror = "Horror"
    musical = "Musical"
    mystery = "Mystery"
    romance = "Romance"
    sci_fi = "Science Fiction"
    sport = "Sport"
    superhero = "Superhero"
    thriller = "Thriller"
    war = "War"
    western = "Western"


# Class to be used for the creation and management of Movie Category table
class MovieCategoryType(Enum):
    action = (1, "Action")
    adventure = (2, "Adventure")
    animation = (3, "Animation")
    biography = (4, "Biography")
    comedy = (5, "Comedy")
    crime = (6, "Crime")
    documentary = (7, "Documentary")
    drama = (8, "Drama")
    family = (9, "Family")
    fantasy = (10, "Fantasy")
    film_noir = (11, "Film Noir")
    history = (12, "History")
    horror = (13, "Horror")
    musical = (14, "Musical")
    mystery = (15, "Mystery")
    romance = (16, "Romance")
    sci_fi = (17, "Science Fiction")
    sport = (18, "Sport")
    superhero = (19, "Superhero")
    thriller = (20, "Thriller")
    war = (21, "War")
    western = (22, "Western")

    def __init__(self, num, label):
        self.num = num
        self.label = label
