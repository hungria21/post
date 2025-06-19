import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock # AsyncMock for async methods
from post import create_post # Assuming post.py is in the same directory

class TestCreatePost(unittest.TestCase):

    @patch('post.client', new_callable=AsyncMock) # Use AsyncMock for the client if its methods are async
    async def test_post_formatting_and_entity_found(self, mock_client):
        # Configure the mock client and its get_entity method
        mock_bot_entity = MagicMock()
        mock_bot_entity.first_name = "TestBot"
        # get_entity is an async method, so its mock should behave like one
        mock_client.get_entity.return_value = mock_bot_entity

        # Inputs for create_post
        bot_username = "testbot"
        language = "English"
        group = "Test Group"
        description = "This is a test description."

        # Expected output
        expected_post = (
            "**TestBot**\n"
            "━━━━━━━━━━\n"
            f"➧ Username: @{bot_username}\n"
            f"➧ Idioma: {language}\n"
            f"➧ Grupo: {group}\n"
            f"➧ Tags:\n\n"
            f"**ℹ️ Descrição:**\n{description}\n"
            "━━━━━━━━━━\n"
            f"**Link:** T.me/{bot_username}"
        )

        # Run the async function create_post
        # Since the test method is now async, we can await directly
        post_content, error = await create_post(bot_username, language, group, description)

        # Assertions
        self.assertIsNone(error)
        self.assertEqual(post_content, expected_post)
        mock_client.get_entity.assert_called_once_with(bot_username)

    @patch('post.client', new_callable=AsyncMock)
    async def test_post_creation_bot_not_found(self, mock_client):
        # Configure mock_client.get_entity to simulate bot not found
        # For an async method, the side_effect should be an exception instance or an async function raising it
        mock_client.get_entity.side_effect = ValueError(f"Error: Bot username 'nonexistentbot' seems invalid or the bot does not exist.")

        # Inputs
        bot_username = "nonexistentbot"
        language = "AnyLang"
        group = "AnyGroup"
        description = "AnyDesc"

        post_content, error = await create_post(bot_username, language, group, description)

        self.assertIsNone(post_content)
        self.assertIsNotNone(error)
        # Check if the specific error message from create_post is returned
        self.assertEqual(error, f"Error: Bot username '{bot_username}' seems invalid or the bot does not exist.")
        mock_client.get_entity.assert_called_once_with(bot_username)

    # It's good practice to also test the case where bot_entity.first_name might be None or empty
    # if the get_entity call succeeds but returns an unexpected entity structure.
    @patch('post.client', new_callable=AsyncMock)
    async def test_post_creation_bot_entity_no_firstname(self, mock_client):
        mock_bot_entity = MagicMock()
        mock_bot_entity.first_name = None # Simulate entity with no first_name
        mock_client.get_entity.return_value = mock_bot_entity

        bot_username = "testbotwithnoname"
        language = "English"
        group = "Test Group"
        description = "This is a test description."

        post_content, error = await create_post(bot_username, language, group, description)

        self.assertIsNone(post_content)
        self.assertIsNotNone(error)
        self.assertEqual(error, "Error: Could not retrieve bot's first name.")
        mock_client.get_entity.assert_called_once_with(bot_username)


if __name__ == '__main__':
    # To run async tests with unittest.main(), you might need a bit more setup
    # or use a test runner that supports asyncio directly like pytest with pytest-asyncio.
    # For simple cases with unittest.main() and recent Python versions,
    # asyncio.run() can be used within each test method if the method itself is not async.
    # However, since I made the test methods async for direct await,
    # running with `python -m unittest test_post.py` is standard.
    # If running `python test_post.py` directly, it might require a runner like:
    # asyncio.run(unittest.main()) # This is not standard, prefer `python -m unittest`
    unittest.main()
