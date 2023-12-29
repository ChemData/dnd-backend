from typing import Optional, Union
from typing_extensions import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic.functional_validators import AfterValidator, BeforeValidator
import generator
import mob_sets
import utils


app = FastAPI(
    title="D&D Utilites",
    description="Some useful tools for DMing.",
    version="0.0.1"
)

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/mob_set_names")
def mob_set_names():
    set_names = [(key, x.name) for key, x in mob_sets.MOB_SETS.items()]
    set_names.sort(key=lambda x: x[1])
    output = [{'value': x[0], 'name': x[1]} for x in set_names]
    return output


@app.get('/environment_set_names')
def environment_set_names():
    set_names = [(key, x['name']) for key, x in generator.ENVIRONMENT_SETS.items()]
    set_names.sort(key=lambda x: x[1])
    output = [{'value': x[0], 'name': x[1]} for x in set_names]
    return output


EmptyStringIsNone = Annotated[Optional[str], AfterValidator(lambda x: None if x == '' else x)]
EmptyIntStringIsNone = Annotated[Optional[int], BeforeValidator(lambda x: None if x == '' else int(x))]
EmptyCrIsNone = Annotated[Optional[utils.CR], AfterValidator(lambda x: None if x == '' else x)]


class EncounterInput(BaseModel):
    party_size: Annotated[int, Field(ge=1)]
    party_level: Annotated[int, Field(ge=1, le=20)]
    difficulty: utils.Difficulty | utils.DifficultySet
    primary_enemy: EmptyStringIsNone = None
    environment_type: EmptyStringIsNone = None
    max_enemies: EmptyIntStringIsNone = None
    minimum_cr: EmptyCrIsNone = None
    roll_hp: bool = True


@app.post("/encounter")
def encounter(data: EncounterInput):
    if data.primary_enemy is None and data.environment_type is None:
        raise HTTPException(status_code=460, detail="You must select either an environment or primary enemy.")
    party = data.party_size * [data.party_level]
    try:
        new_encounter, difficulty, mob_type = generator.hex_encounter(
            data.difficulty, party, data.primary_enemy, data.environment_type, data.max_enemies, data.minimum_cr
        )
    except generator.NoUniqueGroup as e:
        raise HTTPException(status_code=461, detail="The constraints were too tight. Try increasing the max enemies, "
                                                    "reducing the minimum cr, or choosing a different enemy set.")
    encounter_html = new_encounter.html_with_links(data.roll_hp)
    encounter_html = f'<h3>{difficulty.capitalize()} {mob_type.capitalize()}</h3>\n' + encounter_html
    return encounter_html


