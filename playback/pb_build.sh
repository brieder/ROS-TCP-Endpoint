#!/bin/bash
docker build -t brieder/vdt-pb -f Dockerfile.playback --secret id=PAT,src=../.devcontainer/BUILDTOKEN . $*
