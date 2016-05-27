# cug control

![cyber cug control](cybersteuerung_v0.1.0.png)


## Website (js) -> Backend (Flask)

  - connect()
  - disconnect()
  - home(num)
  - homeall()
  - update(json)

## Website (js) <- Backend (Flask)

  - update(json)
  - reset()


## Backend (Pyserial) -> Arduino

  - led(r, g, b, ww)
  - move(leave, pos)
  - home(leave)

## Backend (Pyserial) <- Arduino

  - \#led(r, g, b, ww)
  - \#move(leave, pos)
  - \#home(leave)
