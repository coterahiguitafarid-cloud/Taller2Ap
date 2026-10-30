import argparse
import json
import os
import sys
from urllib.parse import quote

import httpx


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT_SECONDS = 10


def print_result(result):
    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def request_api(method, path, payload=None):
    url = f"{API_BASE_URL}{path}"
    request_options = {"timeout": TIMEOUT_SECONDS}

    if payload is not None:
        request_options["json"] = payload

    try:
        response = httpx.request(method, url, **request_options)
    except httpx.RequestError as error:
        print(f"No se pudo conectar con la API: {error}", file=sys.stderr)
        return 1

    try:
        result = response.json()
    except ValueError:
        result = response.text

    if not response.is_success:
        print(f"Error HTTP {response.status_code}:", file=sys.stderr)
        print_result(result)
        return 1

    print_result(result)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Cliente CLI para la API de aprendices."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="Listar todos los aprendices")

    get_command = commands.add_parser("get", help="Consultar un aprendiz por ID")
    get_command.add_argument("id", help="ID del aprendiz")

    create_command = commands.add_parser("create", help="Registrar un aprendiz")
    create_command.add_argument("--document", required=True)
    create_command.add_argument("--first-name", required=True)
    create_command.add_argument("--last-name", required=True)
    create_command.add_argument("--email", required=True)
    create_command.add_argument("--age", required=True, type=int)
    create_command.add_argument("--program", required=True)
    create_command.add_argument("--record-number", required=True, type=int)

    update_command = commands.add_parser("update", help="Actualizar un aprendiz")
    update_command.add_argument("id", help="ID del aprendiz")
    update_command.add_argument("--first-name")
    update_command.add_argument("--last-name")
    update_command.add_argument("--email")
    update_command.add_argument("--age", type=int)
    update_command.add_argument("--program")

    delete_command = commands.add_parser("delete", help="Eliminar un aprendiz")
    delete_command.add_argument("id", help="ID del aprendiz")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        return request_api("GET", "/trainees/")

    if args.command == "get":
        trainee_id = quote(args.id, safe="")
        return request_api("GET", f"/trainees/{trainee_id}")

    if args.command == "create":
        payload = {
            "document": args.document,
            "first_name": args.first_name,
            "last_name": args.last_name,
            "email": args.email,
            "age": args.age,
            "program": args.program,
            "record_number": args.record_number,
        }
        return request_api("POST", "/trainees/", payload)

    if args.command == "update":
        payload = {
            "first_name": args.first_name,
            "last_name": args.last_name,
            "email": args.email,
            "age": args.age,
            "program": args.program,
        }
        payload = {key: value for key, value in payload.items() if value is not None}

        if not payload:
            parser.error("Indica al menos un campo para actualizar.")

        trainee_id = quote(args.id, safe="")
        return request_api("PUT", f"/trainees/{trainee_id}", payload)

    if args.command == "delete":
        trainee_id = quote(args.id, safe="")
        return request_api("DELETE", f"/trainees/{trainee_id}")

    return 2


if __name__ == "__main__":
    sys.exit(main())