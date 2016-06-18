# cug control

![cyber cug control](cybersteuerung_v0.1.0.png)

# Protocol

## js -> flask

  - connect()
  - disconnect()
  - updtae
  - reset()
  - home()
  - go(drum, index)
  - light(r, g, b, ww)
  - poll()

## flask -> js

  - connected()
  - reset(json)
    - contains all drums and their contents

## flask -> daemon

  - last
    ```
    {
      'changed': '1970-01-01 00:00:00'
    }
    ```
  - status
    ```
    {
      [
        {'0': 'Potsdam Hbf'},
        {'1': 'Berlin Hbf'},
        {'2': ''}
      ],
      [
        {'0': 'Nicht einsteigen'},
        {'1': 'Kurzzug hält hinten'},
        {'2': ''}
      ],
      [
        {'0': 'S1'},
        {'1': 'S2'},
        {'2': ''}
      ]
    }
    ```
  - go $drum $index
  - home
  - light $r $g $b $ww
