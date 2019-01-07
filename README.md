# RRFTracker_Spotnik
Suivi temps réel de l'activité du réseau [RRF](https://f5nlg.wordpress.com/2015/12/28/nouveau-reseau-french-repeater-network/) (Réseau des Répéteurs Francophones). Une video du fonctionnement est visible sur [Youtube](https://www.youtube.com/watch?v=rVW8xczVpEo) ;)

## Principe de fonctionnement

Cette version du RRFTracker permet de suivre en temps réel l'activité du réseau RRF, en utilisant un Rasbperry Pi ou un Orange Pi, communément utilisés sur les Spotniks.

Au repos, si aucune station n'est en émission, RRFTracker affichera sur les 3 première lignes,

* la première ligne: l'indicatif de l'avant dernier noeud étant passé en émission,
* la seconde ligne: l'indicatif du dernier noeud étant passé en émission,
* la troisième ligne: l'heure du dernier passage en émission,

Si un QSO est en cours, RRFTracker affichera sur les 3 première lignes,

* la première ligne: l'indicatif de l'avant avant dernier noeud étant passé en émission,
* la seconde ligne: l'indicatif de l'avant dernier noeud étant passé en émission,
* la troisième ligne: l'indicatif du noeud en cours d'émission.

En complement, sur la ligne centrale, au milieu de l'écran, on retrouve

* le nombre de passages en émission sur la journée (depuis 00h00),
* le temps depuis lequel fonctionne le RRFTracker (uptime),
* le nombre de passage en émission depuis l'allumage du RRFTracker,
* l'indicatif du link le plus actif avec le nombre de passage en émission.

Enfin, en bas de l'écran, on retrouve un histogramme du trafic dans la journée, heure par heure.

## Liste des composants

Voici la liste des composants dont vous aurez besoin:

* 1 Raspberry Pi ou 1 Orange Pi
* 1 écran OLED 0.96" 128x64 type SH1106 ou SSD1306
* 4 cables Dupont femelle / femelle

 
## Schéma de montage

![alt text](https://github.com/armel/RRFTracker_Spotnik/blob/master/doc/RRFTracker.png)