# Nginx reverse proxy

This folder contains the nginx reverse proxy configuration used for the exam project.

The reverse proxy routes traffic to the rover frontend/backend and Grafana through a single entrypoint.

Routes:

- /rover/ -> Rover web application
- /rover/ws/ -> Rover WebSocket endpoint
- /grafana/ -> Grafana

Runtime location on the school server:

/srv/shared/nginx-proxy

Container name:

nginx-proxy
