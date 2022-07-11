ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /code
COPY . /code/
RUN pip install --upgrade pip && pip install pybuilder names essential_generators
RUN pyb -X