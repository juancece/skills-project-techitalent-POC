FROM python:3.10-slim

WORKDIR /app

COPY ./pythonProject /app

COPY ./skills-project-poc-6fa3b9280cec.json /app/skills-project-poc-6fa3b9280cec.json

COPY ./pythonProject/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]