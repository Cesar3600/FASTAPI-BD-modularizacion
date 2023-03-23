
from fastapi import FastAPI, Body,Path,Query, Request,HTTPException,Depends
from fastapi.responses import HTMLResponse,JSONResponse
from pydantic import BaseModel,Field
from typing import Optional,List
from jwt_manager import create_token,validate_token
from fastapi.security import HTTPBearer

import datetime

app = FastAPI()
app.title = 'Mi aplicacion con fastAPI'
app.version = '0.0.3'
actualDate = datetime.datetime.now()
actualYear = actualDate.year

class JWTBearer(HTTPBearer):
   async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403,detail="Credenciales invalidas")

class User(BaseModel):
    email:str
    password:str


class Movie(BaseModel):
    id: Optional[int] = None
    title:str = Field( min_length=5, max_length=15)
    overview:str= Field(min_length=15, max_length=77)
    year: int = Field( le=actualYear)
    ranking:float = Field(ge=1,le=10)
    category:str= Field( max_length=33)
    class Config:
        schema_extra = {
            "example":{
            "id":1,
            "title":"Mi pelicula",
            "overview":"Descripcion de la pelicula",
            "year":actualYear,
            "ranking":5.0,
            "category":"Comedy"
            }
        }



movies = [
    {
      "id":1,
      "title":"Avatar",
      "overview":"En un exuberante planeta llamado Pandora viven los Na'vi, seres que aparentan ser primitivos pero que en realidad son muy evolucionados. Debido a que el ambiente de Pandora es venenoso, los híbridos humanos/Na'vi, llamados Avatares, están relacionados con las mentes humanas, lo que les permite moverse libremente por Pandora. Jake Sully, un exinfante de marina paralítico se transforma a través de un Avatar, y se enamora de una mujer Na'vi.",
      "year":2009,
      "ranking":7.8,
      "category":"Accion"
    },
    {
      "id":2,
      "title":"Stargate",
      "overview":"Un equipo de militares y un científico parten hacia un planeta desconocido a través de una puerta estelar descubierta en una excavación en Egipto.",
      "year":1994,
      "ranking":6.3,
      "category":"Aventura"
    },
    {
      "id":3,
      "title":"Alien",
      "overview":"Una nave carguero recibe una senal de auxilio acudiendo en ayuda sin imaginar que alguien mas abordara ",
      "year":1977,
      "ranking":8.3,
      "category":"Terror"
    },
]


@app.get('/', tags=['home'])
def message():
    return HTMLResponse('<h1>Hello World</h1><p>hey hey hey !!!</p>')


@app.post('/login',tags=['auth'],status_code=200)
def login(user:User) -> User:
    if user.email =="admin@gmail.com" and user.password == "admin":
        token:str = create_token(user.dict())
        return JSONResponse(status_code=200, content=token)


@app.get('/movies', tags=['movies'], response_model=List[Movie],status_code=200,dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content = movies )


@app.get('/movies/{id}', tags=['movies'], response_model=Movie,status_code=200)
def get_movie(id:int = Path(ge=1,le=2000)) -> Movie:
    #return list(filter(lambda movie: movie['id'] == id, movies))
    #return [movie for movie in movies if movie["id"]==id]
    for movie in movies:
        if movie['id'] == id:
            return JSONResponse(status_code=200,content=movie)
    return JSONResponse(status_code=404, content = {"message":f"the id {id} no found"})


@app.get('/movies/',tags=['movies'], response_model=List[Movie],status_code=200)
def get_movies_by_category(category:str= Query(min_length=5,max_length=15)) -> List[Movie]:
    #return [movie for movie in movies if movie['category'] == category]
    #response =  list(filter(lambda movie: movie["category"] == category, movies))
    movies_by_cat = []
    for movie in movies:
        if movie['category'] == category:
            movies_by_cat.append(movie)

    if(len(movies_by_cat) == 0):
        return JSONResponse(status_code=404,content = [])
    
    return JSONResponse(status_code=200,content = movies_by_cat)


@app.post('/movies',tags=['movies'], response_model=dict, status_code=201)
def create_movie(movie:Movie) -> dict:
    movies.append(movie)
    return JSONResponse(status_code=201,content = {"message":"Se ha registrado la pelicula"})


@app.put('/movies/{id}', tags=['movies'], response_model=dict,status_code=200)
def update_movie(id:int, movie:Movie) -> dict:
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['ranking'] = movie.ranking
            item['category'] = movie.category

    return JSONResponse(status_code=200,content = {"message":"Se ha actualizado la pelicula"})

@app.delete('/movies/{id}', tags=['movies'],response_model=dict,status_code=200)
def delete_movie(id:int) -> dict:
    for movie in movies:
        if movie["id"] == id:
            movies.remove(movie)

    return JSONResponse(status_code=200,content={"message":"Se ha eliminado la pelicula"})
    




#@app.put('/movies/{id}', tags=['movies'])




