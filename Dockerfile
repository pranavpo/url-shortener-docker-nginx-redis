FROM python:latest

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . .

RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python3","main.py"]

