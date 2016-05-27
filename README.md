# cug control

![cyber cug control](cybersteuerung_v0.1.0.png)

# Protocol

## SocketIO

  - connect
  - disconnect
  - home
  - homeall
  - update
  - reset

## Serial

Home leave:

  - command: `<leave_id>;home\n`
  - response: `#<leave_id>;home\n`

Move leave:

  - command: `<leave_id>;move;<position>\n`
  - response: `#<leave_id>;move;<position>\n`
