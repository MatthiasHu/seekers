#!/bin/bash -e
# Installs the necessary dependencies (on an Ubuntu-style system), sets up a
# user account, and fires off several VNC servers.

number_of_sessions=5
home_directory=/home/mathecamp

sudo apt-get install -qq -y vnc4server xtightvncviewer openssh-server lxde git \
    libsdl1.2-dev libzzip-dev libsdl-console-dev libsdl-gfx1.2-dev \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-net1.2-dev libsdl-ocaml-dev \
    libsdl-sge-dev libsdl-sound1.2-dev libsdl-ttf2.0-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-net-dev libsdl2-ttf-dev libalien-sdl-dev-perl \
    libsdl-pango-dev libsdl-stretch-dev libsdl2-dev libsdl2-gfx-dev \
    libportmidi-dev python3-pip gedit

id mathecamp >/dev/null || sudo adduser mathecamp --home "$home_directory" --disabled-password

sudo su mathecamp -c "pip3 install pygame"

cd ~mathecamp

sudo mkdir -p .vnc

sudo tee .vnc/xstartup >/dev/null <<'EOF'
#!/bin/bash

xrdb ~/.Xresources
xsetroot -solid grey
export XKL_XMODMAP_DISABLE=1  # for GNOME

(
    cd session$DISPLAY
    x-terminal-emulator -geometry 80x24+10+10 -ls -e ~/seekers/tools/run-interactive.sh &
    gedit -- "$(ls -t -- ai*.py | head -n1)" &
)

exec lxsession
EOF

# Password is "mathecamp"
echo "I/myMdP+Dnw=" | base64 -d | sudo tee .vnc/passwd >/dev/null

sudo chmod +x .vnc/xstartup

sudo chown -R mathecamp.mathecamp .vnc
sudo chmod u=rwx,g=,o= .vnc
sudo chmod u=rx,g=,o= .vnc/passwd

sudo rm -f .vncstartup
sudo ln -s .vnc/xstartup .vncstartup

[ -d "seekers" ] || sudo su mathecamp -c "git clone https://github.com/MatthiasHu/seekers"

for i in $(seq 1 $number_of_sessions); do
    (
        sudo su mathecamp -c "mkdir -p session:$i"
        [ -e "session:$i/simple.py" ] || sudo su mathecamp -c "cp seekers/examples/ai-simple.py session:$i/"
        sudo su mathecamp -c "vncserver -kill :$i" || true
        sudo su mathecamp -c "vncserver :$i"
    ) &
done

wait
