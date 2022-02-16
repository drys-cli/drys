# Setup
FROM python:3.8.12-alpine3.14
RUN adduser -D user
RUN apk add --no-cache make
RUN pip install pipenv setuptools

# Setup source directory
WORKDIR /home/user/tem

USER user

COPY Makefile Pipfile Pipfile.lock setup.py pyproject.toml LICENSE README.md ./
RUN pipenv sync
COPY share share
COPY tem tem

USER root
RUN chown -R user .
# Install tem system-wide
RUN make install-base

USER user

CMD ["pipenv", "run", "sh"]
