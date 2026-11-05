#!/bin/bash
docker build -t voidemulator.azurecr.io/vdt-pb -f Dockerfile.playback --secret id=PAT,src=../.devcontainer/BUILDTOKEN . $*
