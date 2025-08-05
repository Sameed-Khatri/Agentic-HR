FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501 8080

CMD ["bash", "-c", "python main.py & streamlit run home.py --server.port=8501 --server.address=0.0.0.0"]