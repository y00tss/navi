import openai
import config


class OpenAI:
    def __init__(self):
        self.api_token = config.OPENAI_API_KEY
        openai.api_key = self.api_token

    async def check_text(self, text: str) -> bool:
        """Check if the text is friendly or not."""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                            If this text can offend, hurt or contains at least one swear word or a spam, then return 0, 
                            if the text is friendly, then return 1.
                            The text : "{text}"
                        """  # noqa
                },
            ],
            max_tokens=5
        )
        result = response['choices'][0]['message']['content']
        if result == "1":
            return True
        return False

    async def reply_to_comment(self, content: str, comment: str) -> str:
        """Reply to a comment by AI."""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""
                                    This is a post: "{content}", this is a user comment: "{comment}". 
                                    You have to reply to the comment with a friendly message. Maximum 15 words.
                                """  # noqa
                },
            ],
            max_tokens=5
        )
        result = response['choices'][0]['message']['content']
        return result
