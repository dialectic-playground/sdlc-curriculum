# Toolchain image for dialectic-playground/sdlc-curriculum (container-first; see tools/dp-run).
#
# The official Python 3.12 image, plus make and git (for the curriculum checks, the
# BASE-MAKEFILE wiring check, and the consistency checks). The base image is pinned by
# multi-architecture index digest; Dependabot (docker) keeps it current.
FROM docker.io/library/python:3.12-slim-trixie@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1

RUN apt-get update \
    && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*

ENV DP_IN_CONTAINER=1
