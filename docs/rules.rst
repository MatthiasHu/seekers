.. Seekers rules documentation file

======
Regeln
======

Hier konkretisieren wir die genauen Regeln von Seekers:

1. Das *Feld* ist ein Torus der Größe 768 x 768 Pixeln.
2. Der Betrag der Beschleunigung ist konstant und nicht beeinflussbar und es gibt eine Maximalgeschwindigkeit. Das
bedeutet, dass man beim Festlegen eines Ziels für einen Seeker nur die *Richtung* der Beschleunigung beeinflusst. Eine
Ausnahme ist das Beschleunigen auf die eigene Position, die einen Seeker nicht beschleunigen lässt.
3. Es gibt Reibung. Das heißt ein Seeker, welcher nicht beschleunigt, wird langsamer bis dieser stehen bleibt.
4. Der Magnet eines Seekers kann aus (*off*), anziehend (*attractive*) oder abstoßend (*repelling*) sein.
5. Magnetfelder können nur Goals beeinflussen, nicht aber andere Seeker.
6. Kollisionen zwischen Seekers und Goals sind elastisch. Insbesondere sind beide Objekte Kreise mit
nicht-verschwindendem Radius.
7. Wenn zwei Seeker mit Magnetfeldern kollidieren, können diese Seeker kurzzeitig deaktiviert werden und sind dann
nicht kontrollierbar. Wenn beide Seeker ihr Magnetfeld aktiviert haben, bekommen beide diese Strafzeit, wenn nur einer
das Magnetfeld an, wird nur dieser kurz ausgeschaltet.
8. Sobald ein Goal für eine gewisse Zeit in der Basis eines Spielers ist, erhält dieser einen Punkt. Das Goal
verschwindet dann und wird an einem zufälligen Punkt auf dem Feld neu erstellt.
9. Gewonnen hat z.B. wer nach einer vorher festgelegten Zeit die meisten Punkte hat.

Parameter
=========

Folgende Parameter sind momentan hart-kodiert, werden aber in der Zukunft konfigurierbar gemacht:

* Feldgröße
* Anzahl der Seeker
* Anzahl der Goals
* Gewinnbedingung
* Basisgröße
* Stärke der anziehenden Magnete
* Stärke der abstoßenden Magnete
* Beschleunigung
* Reibungskoeffizient
* Kollisionsstrafen
* Zeit, nach der ein Goal in der Basis einen Punkt gibt

Gewinnbedingungen
=================

Momentan gibt es keine echten implementierten Gewinnbedingungen, jedoch existiert ein
`Issue <https://github.com/MatthiasHu/seekers/issues/18>` zum Hinzufügen dieses Features.

