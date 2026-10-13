# Toolchain image for dialectic-playground/sdlc-curriculum (container-first; see tools/dp-run).
#
# The official Python 3.12 image, plus make and git (for the curriculum checks, the
# BASE-MAKEFILE wiring check, and the consistency checks). The base image is pinned by
# multi-architecture index digest; Dependabot (docker) keeps it current.
FROM docker.io/library/python:3.14-slim-trixie@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

RUN apt-get update \
    && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*

ENV DP_IN_CONTAINER=1
