FROM python:3
LABEL maintainer="Matthew Turi <mxt9495@rit.edu>"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./activity2.py" ]