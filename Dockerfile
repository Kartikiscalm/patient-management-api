FROM python:3.14.1
WORKDIR /main
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . . 
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
#fastapi port 8000 pe kaam karta hai