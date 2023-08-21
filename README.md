# fastapi-celery
 FastAPI with SQLModel, Celery, RabbitMQ, PostgreSQL and Docker Compose.
 This project uses Celery workers to periodically update database with the given Google Sheets spreadsheet content.

## Caution
This project is **not** production-ready and there are *known errors* need to be fixed.


To run this project in your local environment you need Python and Docker Compose installed in your machine.
Steps:
1. Clone this repository
2. Run `sudo docker compose up --build` to build and run project
3. Open `http://localhost:8000/ping` in your browser.
If you see {"ping": "pong"}, then you're all set!


Main usage:
1. The celery task will run automatically every 2 hours.
To start synchronization process manually, send GET request to this URL:
`http://localhost:8000/api/start-worker`
You will get a `task_id` which you can use to get the 

2. You can check all entries saved in db from this URL:
`http://localhost:8000/api/entities`
Add `limit` and `offset` params for pagination purposes. Default values are `limit=10` and `offset=0`.


Known errors:
- Spreadsheet and database comparison not always work as expected. This will result in data being added with the same id, hence fail the query. (I need to check data cleaning in the spreadsheet)
- If the spreadsheet is empty or file is not found, the task will fail.
- If the spreadsheet is not in the correct format, the task will fail.
- If the database is not available, the task will fail.
- If the database is not in the correct format, the task will fail.


TODO list:
- Write unit tests
- Hard coded constants need to be written in env vars
- Create docker compose file for production environment
- Configure Poetry, Alembic, Black
- Use multi-stage Docker image and non-root user
- Add Traefik
- Add CI/CD
- Edit readme, .gitignore and .dockerignore files


Would be nice to add:
- An endpoint for checking celery task result by task id.
- An endpoint to change the celery task schedule
- An endpoint to change spreadsheet download link
