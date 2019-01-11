# RRFTracker_Spotnik
Suivi temps réel de l'activité du réseau [RRF](https://f5nlg.wordpress.com/2015/12/28/nouveau-reseau-french-repeater-network/) (Réseau des Répéteurs Francophones) pour Spotnik. Une video du fonctionnement est visible sur [Youtube](https://www.youtube.com/watch?v=rVW8xczVpEo) ;)

## Présentation

Cette version du RRFTracker et une évolution d'un [premier projet](https://github.com/armel/RRFTracker) réalisé mi novembre 2018 à partir d'un Nodemcu ESP8266 et d'un écran LCD 16x2.

Il permet de suivre en temps réel l'activité du réseau [RRF](https://f5nlg.wordpress.com/2015/12/28/nouveau-reseau-french-repeater-network/) (Réseau des Répéteurs Francophones), mais également du [FON](http://www.f1tzo.com/) (French Open Networks), en utilisant un Rasbperry Pi ou un Orange Pi Zero et un écran OLED type SH1106 ou SSD1306 piloté par I2C. Ces écrans ont un QSJ de moins de 5€.

Pour le moment, cette version du RRFTracker prend en charge [2 tailles d'écrans](http://www.dsdtech-global.com/2018/05/iic-oled-lcd-u8glib.html). 

- 1.3" 128 x 64
- 0.9" 128 x 32

Ce dispositif peut donc être associé sans (_trop de_) difficulté à un Spotnik Gamma, Delta, etc. afin de profiter d'un minimum de remontée d'informations, à l'image des Hotspots MMDVM type ZUMspot, Jumbo SPOT, etc. si precieux aux porteurs de casques de chantier... j'ai nommé les DMRistes ;)

En complément, à noter l'existence du projet [Spotnik2hmi](https://github.com/F8ASB/spotnik2hmi), porté par F8ASB (Juan), F5SWB (Dimitri) et F0DEI (Toufik) et basé sur l'utilisation d'un écran type Nextion. Du fait des caractéristiques beaucoup plus évoluées de ce type d'écrans tactiles, ce projet offre plus de possibilités, notamment en terme d'interactivité (changement de salon, etc.). Je ne peux que vous encourager à le tester, si le QSJ d'un écran Nextion ne vous fait pas peur. 

## Principe de fonctionnement

### Ecran 128 x 32
Au repos, si aucune station n'est en émission, le RRFTracker affichera,

* l'indicatif des 2 derniers noeuds étant passés en émission,
* l'heure du dernier passage en émission.

Si un QSO est en cours, le RRFTracker affichera,

* l'indicatif des 2 derniers noeuds étant passés en émission,
* l'indicatif du noeud en cours d'émission.

Enfin, en haut à droite de l'écran, le RRFTraker affiche l'heure courante.

### Ecran 128 x 64

En complément des informations visibles sur un écran 128 x 32, si votre écran dispose d'une résolution 128 x 64 pixels, des informations supplémentaires seront disponibles.

Sur la ligne centrale, au milieu de l'écran, on dispose,

* du nombre de passages en émission sur la journée (depuis 00h00),
* du temps depuis lequel fonctionne le RRFTracker (uptime),
* du nombre de passages en émission depuis l'allumage du RRFTracker,
* de l'indicatif du noeud le plus actif avec le nombre de passage en émission,
* de la température du Spotnik.

Pour finir, en bas de l'écran, on retrouve l'histogramme du trafic dans la journée, heure par heure.

À noter qu'à minuit, le nombre de passages en émission sur la journée ainsi que l'histogramme sont réinitialisés (à zéro). 

## Post installation sur Spotnik 1.9

### Installation de paquets complémentaires

En partant de la version 1.9 de Spotnik, commencez par cloner ce projet dans le répertoire /opt. Donc, depuis une connexion SSH, lancez les commandes suivantes:

`cd /opt`

Puis, 

`git clone https://github.com/armel/RRFTracker_Spotnik.git`

Il faut également procéder à l'installation de quelques paquets complémentaires. Toujours depuis une connexion SSH, lancez les commandes suivantes:

`sudo apt-get install i2c-tools libi2c-dev python-smbus python-pip python-dev python-imaging`

`sudo apt-get install libfreetype6-dev libjpeg-dev build-essential`

`sudo pip install --upgrade setuptools`

`sudo -H pip install --upgrade luma.oled`

Enfin, si ce n'est pas déjà fait, il reste à activer le support du protocole I2C afin de pouvoir dialoguer avec l'écran OLED. Ce sera l'étape la plus compliquée...

### Activation du support I2C sur Raspberry Pi

Utilisez l'utilitaire `raspi-config`. Une fois lancé,

* option 5 - Interfacing Options
* sous option P5 - I2C
* répondez oui ;)
 

### Activation du support I2C sur Orange Pi Zero

C'est un peu plus compliqué ;) Vous allez devoir éditer le fichier `/boot/script.fex`. Ligne 147, changer la ligne `twi_used = 0` par `twi_used = 1`.

Puis exécutez la commande `fex2bin /boot/script.fex /boot/script.bin` et enfin rebootez...

### Vérification

Pour finir et vérifier que tout est pret, une fois l'écran connecté (voir schéma), exécutez la commande suivante:

`i2cdetect -y 0`

Cette commande devrait retourner quelque chose comme:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
40: -- -- -- -- -- -- -- -- UU -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

Votre écran est bien raccordé. Et il utilise le port 0 et l'adresse 3c. Si la commande n'a pas fonctionné, essayez:

`i2cdetect -y 1`

## Lancement

Le script `RRFTracker.py` peut recevoir des arguments au lancement.

```
root@spotnik:/opt/RRFTracker_Spotnik# python RRFTracker.py -h
usage: RRFTracker.py
-h, --help
-p, --i2c-port I2C_PORT
-a, --i2c-address I2C_ADDRESS
-d, --display DISPLAY (choose from 'sh1106', 'ssd1306')
-r, --room ROOM (choose from 'RRF', 'TEC', 'FON')
```

Par défaut, sans argument, le RRFTracker va démarrer avec les paramètres suivants,

- i2c_port = 0
- i2c_address = 0x3C
- display = sh1106  (en 128 x 64)
- room = RRF

Cela revient à lancer le RRFTracker avec les arguments suivants,

`python /opt/RRFTracker_Spotnik/RRFTracker.py -p 0 -a 0x3C -d sh1106 -room RRF`

Il est donc possible d'affiner les paramètres, en fonction de ce que vous retournera la commande `i2cdetect` décrite ci dessus.

Par exemple, avec les paramètres suivants,

- i2c_port = 1
- i2c_address = 0x3C
- display = ssd1306  (en 128 x 32)
- room = RRF

Il vous siffira de lancer le RRFTracker avec les arguments suivants,

`python /opt/RRFTracker_Spotnik/RRFTracker.py -p 1 -d ssd1306`

Notez qu'il n'est pas nécessaire de préciser l'i2c_address et la room, puisque ce sont déjà les valeurs par défaut.

Et si vous voulez le laisser tourner en tache de fond, utilisez la commande `nohup` et l'_esperluette_ ;) Par exemple, 

`nohup python /opt/RRFTracker_Spotnik/RRFTracker.py -p 0 -a 0x3C -d sh1106 &`

Et voilà ;)

## Liste des composants

Voici la liste des composants dont vous aurez besoin:

* 1 Raspberry Pi ou 1 Orange Pi Zero
* 1 écran OLED 1.3" 128 x 64 ou 0.9" 128 x 32, type SH1106 ou SSD1306
* 4 cables Dupont femelle / femelle
 
## Schéma de montage

![alt text](https://github.com/armel/RRFTracker_Spotnik/blob/master/doc/RRFTracker_RPI.png)

![alt text](https://github.com/armel/RRFTracker_Spotnik/blob/master/doc/RRFTracker_OPI.png)