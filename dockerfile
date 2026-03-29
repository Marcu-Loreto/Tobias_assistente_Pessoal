FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN pip install uv
RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8000", "--server.address=0.0.0.0"]