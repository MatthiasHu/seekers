#!/bin/bash -e
# Intended to be called as user "mathecamp", as setup by setup-vnc.sh.
# Sven's Trueskill daemon calls this script.

player1="$1"
player2="$2"

function error {
    echo "$1" >&2
    exit 1
}

cd

for i in session*; do
    if [ -e "$i/name.txt" ]; then
        name="$(cat "$i/name.txt")"
        if [ "$name" = "$player1" ]; then
            session1="$i"
        elif [ "$name" = "$player2" ]; then
            session2="$i"
        fi
    fi
done

[ -n "$session1" ] || error "Session of player '$player1' not found."
[ -n "$session2" ] || error "Session of player '$player2' not found."

bot1="$(ls -t -- $session1/ai*.py | head -n1)"
bot2="$(ls -t -- $session2/ai*.py | head -n1)"

[ -n "$bot1" ] || error "No bot for player '$player1' found."
[ -n "$bot2" ] || error "No bot for player '$player2' found."

winning_bot="$(python3 ~/seekers/src/seekers.py "$bot1" "$bot2")"

if [ "$winning_bot" = "$bot1" ]; then
    echo "$player1"
elif [ "$winning_bot" = "$bot2" ]; then
    echo "$player2"
fi
