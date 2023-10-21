FROM python:3.10-alpine as development

EXPOSE 8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apk add --no-cache ffmpeg
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

RUN mkdir app
WORKDIR /app
COPY ./app /app


RUN adduser -u 5678 --disabled-password --gecos "" user && chown -R user /app
USER user
CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]