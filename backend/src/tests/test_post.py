from httpx import AsyncClient


class TestPublicUser:

    async def test_add_post(self, ac_fake: AsyncClient):
        response = await ac_fake.post("/posts/", json={
            "title": "Title",
            "content": "Content Good",
        })
        assert response.status_code == 401

    async def test_get_all_posts(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/posts/all")
        assert response.status_code == 401

    async def test_get_all_friendly_posts(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/posts/all_friendly")
        assert response.status_code == 401

    async def test_get_posts_by_user(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/posts/user")
        assert response.status_code == 401

    async def test_get_post_by_id(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/posts/1")
        assert response.status_code == 401

    async def test_update_post_by_not_allowed_method(self, ac_fake: AsyncClient):
        response = await ac_fake.put("/posts/1", json={
            "title": "Title",
            "content": "Content Good",
            "auto_answer": False,
            "delay_answer": 30
        })
        assert response.status_code == 405

    async def test_update_post_by_patch(self, ac_fake: AsyncClient):
        response = await ac_fake.patch("/posts/1", json={
            "title": "Title",
            "content": "Content Good",
            "auto_answer": False,
            "delay_answer": 30
        })
        assert response.status_code == 401


class TestAuthenticatedUser:

    async def test_add(self, ac: AsyncClient):
        response = await ac.post("/posts/", json={
            "title": "Title",
            "content": "Content Good",
        })
        assert response.status_code == 201
        response_json = response.json()
        assert response_json["description"] == "Post created successfully"

    async def test_update_post_by_patch(self, ac: AsyncClient):
        response = await ac.patch("/posts/1", json={
            "title": "Title",
            "content": "Content GoodDDDDDD",
            "post_id": 1
        })
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["description"] == "Post changed successfully"

    async def test_update_post_by_patch_with_toxic_words(self, ac: AsyncClient):
        response = await ac.patch("/posts/1", json={
            "title": "Title",
            "content": "Fuck you",
            "post_id": 1
        })
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["description"] == "Post was updated but it is not friendly, change the content"  # noqa

    async def test_get_all_posts(self, ac: AsyncClient):
        response = await ac.get("/posts/all")
        assert response.status_code == 200
        response_json = response.json()
        assert isinstance(response_json, list)
        assert len(response_json)
        post = response_json[0]
        assert post['content'] == "Fuck you"
        assert ~post['friendly']

    async def test_get_all_friendly_posts(self, ac: AsyncClient):
        response = await ac.get("/posts/all_friendly")
        assert response.status_code == 200

    async def test_get_posts_by_user(self, ac: AsyncClient):
        response = await ac.get("/posts/user")
        assert response.status_code == 200

    async def test_get_post_by_id(self, ac: AsyncClient):
        response = await ac.get("/posts/1")
        assert response.status_code == 200

    async def test_add_one_more(self, ac: AsyncClient):
        response = await ac.post("/posts/", json={
            "title": "Title",
            "content": "Content Good Super",
        })
        assert response.status_code == 201
        response_json = response.json()
        assert response_json["description"] == "Post created successfully"

    async def test_delete_post(self, ac: AsyncClient):
        response = await ac.delete("/posts/1")
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["description"] == "Post deleted successfully"
