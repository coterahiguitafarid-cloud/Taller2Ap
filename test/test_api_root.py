import asyncio
import unittest

from fastapi.routing import APIRoute
from techgear_api.main import app


class RootRouteTests(unittest.TestCase):
    def test_root_returns_api_status_message(self) -> None:
        root_route = next(
            route
            for route in app.routes
            if isinstance(route, APIRoute) and route.path == "/"
        )
        response = asyncio.run(root_route.endpoint())

        self.assertIn("GET", root_route.methods)
        self.assertEqual(
            response,
            {"message": "¡API de TechGear funcionando correctamente!"},
        )


if __name__ == "__main__":
    unittest.main()
