# Default dockerfile for ad-hoc testing without affecting your actual system

# Setup
FROM alpine:3.14.3
RUN adduser -D user
RUN apk add python3 py3-setuptools make

WORKDIR /home/user/tem

# Copy files into container
COPY tem tem
COPY conf conf
COPY Makefile setup.py pyproject.toml LICENSE README.md ./

# Install and make ready for interactive testing
RUN make install-base PREFIX=/usr
RUN chown -R user .
USER user
