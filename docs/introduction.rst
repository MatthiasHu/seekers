.. Seekers Einführung Dokumentation

==========
Einführung
==========

Seekers ist ein Spiel, in dem *n* Spieler *m* Magnete, sogenannte *Seekers* steuern, die zufällig erscheinende *Goals*
einsammeln und zur ihrer Heimatbasis, ihrer *Base*, bringen müssen. Wenn sie die Goals für eine gewisse Zeit in ihrer
Base halten können, erhalten die Spieler einen Punkt. Danach verschwindet das Goal und ein neues entsteht an einem
zufälligen Ort auf dem Feld.

Die Seekers werden durch ein selbstgeschriebenes Programm gesteuert, welchen Zugriff auf den Zustand des Spiels hat und
Logik anwenden kann um Entscheidungen zu treffen. Das heißt, dass jede Runde (wovon es ca. 20 pro Sekunde gibt) ein
Spieler

* die Position, Geschwindigkeit sowie die Zielposition jedes Seekers auf dem Feld,
* die Position und Geschwindigkeit jedes Goals und
* den Zustand der Magneten aller Seekers

kennt. Damit kann der Spieler entscheiden, was seine Seeker machen, d.h. er oder sie kann

* das Ziel der eigenen Seekers sowie
* den Status der Magneten der eigenen Seekers

beeinflussen. Der Code der Spieler wird jede Runde aufgerufen und die letzten Eigenschaften der entsprechenden Objekte
werden auf den Zustand des Spiels angewendet. Das *Feld*

=========
Benutzung
=========

Seekers kann wie folgt gestartet/gespielt werden.