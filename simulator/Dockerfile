FROM python:3.11-slim
WORKDIR /sim
COPY simulate_prs.py .
RUN pip install --no-cache-dir requests flask
EXPOSE 9000
CMD ["python", "simulate_prs.py"]
