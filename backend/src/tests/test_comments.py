from httpx import AsyncClient

from services.logger import Logger
import logging

logger = Logger(__name__, level=logging.INFO, log_to_file=True, log_dir='logger',
                filename='tests_comments.log').get_logger()


class TestPublicUser:

    async def test_add_comment(self, ac_fake: AsyncClient):
        response = await ac_fake.post("/comments/", json={
            "content": "Content Good",
            "post_id": 2,
            "user_id": 1
        })
        assert response.status_code == 401

    async def test_get_all_comments(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/comments/all")
        assert response.status_code == 401

    async def test_get_all_friendly_comments(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/comments/all_friendly")
        assert response.status_code == 401

    async def test_get_comments_by_user(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/comments/user")
        assert response.status_code == 401

    async def test_get_comments_by_post_id(self, ac_fake: AsyncClient):
        response = await ac_fake.get("/comments/1")
        assert response.status_code == 401

    async def test_update_comment_by_not_allowed_method(self, ac_fake: AsyncClient):
        response = await ac_fake.put("/comments/1", json={
            "content": "Updated content",
        })
        assert response.status_code == 405

    async def test_update_comment_by_patch(self, ac_fake: AsyncClient):
        response = await ac_fake.patch("/comments/1", json={
            "content": "Updated content",
        })
        assert response.status_code == 401

    async def test_delete_comment(self, ac_fake: AsyncClient):
        response = await ac_fake.delete("/comments/1")
        assert response.status_code == 401


class TestAuthenticatedUser:

    # async def test_add_comment(self, ac: AsyncClient):
    #     response = await ac.post("/comments/", json={
    #         "content": "Content Good",
    #         "post_id": 2,
    #     })
    #     assert response.status_code == 201
    #     response_json = response.json()
    #     logger.info(f'TEST {response_json}')
    #     logger.error(f'TEST {response_json}')
    #     assert response_json["description"] == "Comment created successfully"

    async def test_update_comment_by_patch(self, ac: AsyncClient):
        response = await ac.patch("/comments/2", json={
            "content": "Updated content for comment 2",
        })
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["description"] == "Comment updated successfully"

    # async def test_add_toxic_comment(self, ac: AsyncClient):
    #     response = await ac.post("/comments/", json={
    #         "content": "Content Bad Fuck!",
    #         "post_id": 2,
    #     })
    #     assert response.status_code == 201
    #     response_json = response.json()
    #     assert response_json["description"] == "Comment was created but not friendly, change the content"  # noqa

    # async def test_delete_comment(self, ac: AsyncClient):
    #     response = await ac.delete("/comments/2")
    #     assert response.status_code == 200
    #     response_json = response.json()
    #     logger.info(f'TEST {response_json}')
