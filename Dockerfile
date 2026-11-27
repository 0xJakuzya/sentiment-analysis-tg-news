FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu 'torch>=2.6'
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY src/ src/
COPY config/ config/
CMD ["python", "main.py"]