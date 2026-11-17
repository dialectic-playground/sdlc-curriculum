# Toolchain image for dialectic-playground/sdlc-curriculum (container-first; see tools/dp-run).
#
# The official Python 3.12 image, plus make and git (for the curriculum checks, the
# BASE-MAKEFILE wiring check, and the consistency checks). The base image is pinned by
# multi-architecture index digest; Dependabot (docker) keeps it current.
FROM docker.io/library/python:3.12-slim-trixie@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

# Debian keeps only the current version of each package, so apt versions cannot be pinned
# reproducibly; the base image is pinned by digest instead.
# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*

ENV DP_IN_CONTAINER=1
