from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


class CreateUserResponse(BaseModel):
    user_id: int

class User(BaseModel):
    username: int
    liked_posts: list[int] = None


class FullUserProfile(User):
    short_description: str
    long_description: str

class UserBio(BaseModel):
    short_description: str
    long_description: str


class MultipleUsersResponse(BaseModel):
    users: list[FullUserProfile]


profile_infos = {
    0: {
        "short_description": "Short Test",
        "long_description": "Long Test"
    },
    1: {
         "short_description": "Short Test 1",
         "long_description": "Long Test 1"
     }
}

users_content = {
    0:  {
        "username": 0,
        "liked_posts": [1, 2, 3]
    },
    1: {
        "username": 1,
        "liked_posts": [4,5,6]
     }
 }


def get_userinfo(user_id: int = 0) -> FullUserProfile:
    profile_info = profile_infos[user_id]
    user_content = users_content[user_id]
    user = User(**user_content)
    full_user_profile = {
        **profile_info,
        **user.dict()
    }
    return FullUserProfile(**full_user_profile)


def create_update_user(full_profile_info: FullUserProfile, new_user_id: Optional[int] = None) -> int:
    if new_user_id is None:
        new_user_id = len(profile_infos)
    username = full_profile_info.username
    liked_posts = full_profile_info.liked_posts
    short_description = full_profile_info.short_description
    long_description = full_profile_info.long_description

    users_content[new_user_id] = {"username": username, "liked_posts": liked_posts}
    profile_infos[new_user_id] = {"short_description": short_description, "long_description": long_description}

    return new_user_id


def get_all_users_paginated(start: int, limit: int) -> list[FullUserProfile]:
    list_of_users = []
    keys = list(profile_infos.keys())
    for index in range(0, len(keys),1):
        if index < start:
            continue
        current_key = keys[index]
        user = get_userinfo(current_key)
        list_of_users.append(user)
        if len(list_of_users) >= limit:
            break

    return list_of_users


def delete_user(user_id: int) -> None:
    del profile_infos[user_id]
    del users_content[user_id]


def update_bio(user_bio: UserBio, user_id: int):
    short_description = user_bio.short_description
    long_description = user_bio.long_description
    profile_infos[user_id] = {"short_description": short_description, "long_description": long_description}
    return None



@app.get("/user/{user_id}")
def get_user_by_id(user_id: int):

    full_user_profile = get_userinfo(user_id)
    return full_user_profile


@app.get("/users", response_model=MultipleUsersResponse)
def display_all_users_paginated(start: int = 0, limit: int = 5):
    users = get_all_users_paginated(start, limit)
    formatted_users = MultipleUsersResponse(users=users)
    return formatted_users


@app.post("/users", response_model=CreateUserResponse)
def add_user(full_profile_info: FullUserProfile):
    user_id = create_update_user(full_profile_info)
    created_user = CreateUserResponse(user_id=user_id)
    return created_user


@app.put("/user/{user_id}")
def update_user(user_id: int, full_profile_info: FullUserProfile):
    create_update_user(full_profile_info, user_id)
    return None


@app.delete("/user/{user_id}")
def remove_user(user_id: int):
    delete_user(user_id)


@app.patch("/user/{user_id}", response_model=FullUserProfile)
def patch_user(user_id: int, user_bio: UserBio):
    update_bio(user_bio, user_id)
    return get_user_by_id(user_id)
