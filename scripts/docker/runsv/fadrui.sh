#!/bin/bash

echo "Starting web ui"
chmod +x /opt/fadr/fadr/runui.py
exec /sbin/setuser fadr /bin/python3 /opt/fadr/fadr/runui.py
