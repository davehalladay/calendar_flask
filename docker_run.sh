#!/usr/bin/env bash

docker run -d -p 5000:5000 --name="calendar_flask" --restart=always --env-file ./environment_variables calendar_flask:latest