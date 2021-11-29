# TODO change to an exact version when possible
FROM tem:latest

USER root

# Prepare system-level dependencies
# ---------------------------------
RUN apk add bats git
# Required in order to run BATS under make
RUN apk add ncurses
# Required by some tests that use the 'unbuffer' command
RUN apk add expect

# Prepare user-level environment
# ------------------------------
USER user
RUN pipenv sync --dev
WORKDIR tests

# Prepare tests directory
# -----------------------
USER root
# For easier manual inspection of the directory structure created by tests
RUN mkdir /t && chown -R user /t
RUN mkdir -p cli \
    && chown -R user .
# Flag for make
ENV __TEM_TESTS_INSIDE_DOCKER_CONTAINER__ true
COPY . .

USER user
CMD make all; cd /t && exec sh
