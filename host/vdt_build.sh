#!/bin/bash
docker build -t brieder/vdt -f .devcontainer/Dockerfile --secret id=PAT,src=.devcontainer/BUILDTOKEN .
