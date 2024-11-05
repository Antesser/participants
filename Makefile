start:
	uvicorn main:app --reload
compose:
	docker compose up --build