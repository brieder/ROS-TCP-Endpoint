#!/bin/bash
docker build -t brieder/vdt -f .devcontainer/Dockerfile --no-cache --secret id=PAT,src=.devcontainer/BUILDTOKEN .
