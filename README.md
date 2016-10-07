![Alt text](/doc/smallbot.png?raw=true)
# FLATBOT
    Simple daemon converts  Incoming:SFTP/XLS/CSV  to  Outgoing:HTTP/JSON

Flatbot serves as a simple container image which exposes an SFTP flat-file upload destination and converts the incoming files into HTTP events. The incoming flat files are decomposed into rows which are sent onwards as individual JSON clusters.
