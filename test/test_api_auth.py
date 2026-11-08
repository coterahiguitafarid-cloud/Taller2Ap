import unittest
import os
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from techgear_api.auth import require_portal_token
from techgear_api.database import Settings


class PortalTokenTests(unittest.TestCase):
    def test_existing_mongo_url_environment_name_is_supported(self) -> None:
        with patch.dict(
            os.environ,
            {"MONGO_URL": "mongodb://localhost/techgear"},
            clear=True,
        ):
            settings = Settings(_env_file=None)
        self.assertEqual(settings.mongodb_uri, "mongodb://localhost/techgear")

    def test_missing_server_token_fails_closed(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(HTTPException) as raised:
                require_portal_token(None)
        self.assertEqual(raised.exception.status_code, 503)

    def test_invalid_token_is_rejected(self) -> None:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="wrong-token",
        )
        with patch.dict("os.environ", {"TECHGEAR_API_TOKEN": "correct-token"}):
            with self.assertRaises(HTTPException) as raised:
                require_portal_token(credentials)
        self.assertEqual(raised.exception.status_code, 403)

    def test_valid_portal_token_is_accepted(self) -> None:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="correct-token",
        )
        with patch.dict("os.environ", {"TECHGEAR_API_TOKEN": "correct-token"}):
            self.assertIsNone(require_portal_token(credentials))


if __name__ == "__main__":
    unittest.main()
