# RRFDisplay
Suivi temps réel de l'activité du réseau [RRF](https://f5nlg.wordpress.com/2015/12/28/nouveau-reseau-french-repeater-network/) (Réseau des Répéteurs Francophones) pour Spotnik. Une video du fonctionnement est visible sur [Youtube](https://www.youtube.com/watch?v=H2tEJSdAOHU) ;)

## Présentation

Cette version du RRFDisplay et une évolution d'un [premier projet](https://github.com/armel/RRFLcd) réalisé mi novembre 2018 à partir d'un Nodemcu ESP8266 et d'un écran LCD 16x2.

Il permet de suivre en temps réel l'activité du réseau [RRF](https://f5nlg.wordpress.com/2015/12/28/nouveau-reseau-french-repeater-network/) (Réseau des Répéteurs Francophones), mais également du [FON](http://www.f1tzo.com/) (French Open Networks), en utilisant un Raspberry Pi 3 ou un Orange Pi Zero et 

- un écran type SH1106, SSD1306 ou SSD1327 piloté par I2C
- un écran de type SSD1351 ou ST7735 piloté par SPI

Les écrans type SH1106 ou SSD1306 ont un QSJ de moins de 5€. Les écrans type SSD1327 et ST7735 sont un peu plus onéreux, mais coûte moins de 8€. Quant aux écrans type SSD1351, compter environ 15€. Le QSJ était une des contraintes de mon cahier des charges. À noter que vous pouvez les trouver moins cher sur des boutiques chinoises, si vous acceptez de patienter 30 à 60 jours pour la livraison.  

Cette version du RRFDisplay prend en charge [3 tailles d'écrans](http://www.dsdtech-global.com/2018/05/iic-oled-lcd-u8glib.html) OLED et 2 résolutions. 

- 1.50" en 128 x 128
- 1.30" en 128 x 64
- 0.96" en 128 x 64 

La résolution 128 x 128 en 1.50" est disponible en utilisant des écrans de type [SSD1327](https://www.waveshare.com/wiki/1.5inch_OLED_Module) ou [SSD1351](https://www.waveshare.com/wiki/1.5inch_RGB_OLED_Module). Le premier fonctionne en I2C et gère des niveaux de gris. Le second fonctionne en SPI et supporte 65K couleurs. Ce sont mes 2 écrans préférés.

> Attention, les écrans SSD1327 pilotés en I2C ne fonctionnent que sur l'Orange Pi Zero. Quant aux écrans SSD1351 ou ST7735 piloté par SPI, je n'ai réussi à les faire fonctionner que sur Raspberry Pi 3.

Ce dispositif peut donc être associé sans (_trop de_) difficulté à un Spotnik Gamma, Delta, etc. afin de profiter d'un minimum de remontée d'informations, à l'image des Hotspots MMDVM type ZUMspot, Jumbo SPOT, etc. si precieux aux porteurs de casques de chantier... j'ai nommé les DMRistes ;)

En complément, à noter l'existence du projet [Spotnik2hmi](https://github.com/F8ASB/spotnik2hmi), porté par F8ASB (Juan), F5SWB (Dimitri) et F4ICR (Pascal) et basé sur l'utilisation d'un écran type Nextion. Du fait des caractéristiques beaucoup plus évoluées de ce type d'écrans tactiles, ce projet offre plus de possibilités, notamment en terme d'interactivité (changement de salon, etc.). Je ne peux que vous encourager à le tester, si le QSJ d'un écran Nextion ne vous fait pas peur. 

## Principe de fonctionnement

### Ecran 128 x 64

Au repos, si aucune station n'est en émission, le RRFDisplay affichera les informations suivantes :

Sur la première ligne, en haut de l'écran, on dispose,

* du nombre de passages en émission sur la journée (depuis 00h00),
* du nombre de links actifs,
* du nombre de links total,
* du temps d'émission cumulée total sur la journée,
* du salon ou de l'indicatif suivi par le RRFDisplay,
* de l'heure du dernier passage en émission.

En haut à droite, l'heure et le salon courant s'affiche alternativement.

Sur les 3 lignes suivantes, au milieu de l'écran, figure les 3 derniers indicatifs des stations qui sont passées en émission.

Enfin, en bas de l'écran, on retrouve l'histogramme du trafic dans la journée, heure par heure.

Alternativement, si aucune station n'est en émission, le RRFDisplay affichera différents écrans complémentaires:

* l'historique des 5 derniers noeuds étant passés en émission ainsi que l'horodatage,
* l'historique des 5 noeuds les plus actifs ainsi que la durée cumulée de passage en émission,
* l'état du Spotnik (sur 2 pages): architecture, uptime, noyau, charge et fréquence du CPU, température, adresse IP, occupation mémoire et disque, version,
* la configuration courante (sur 2 pages).

Enfin, si une station passe en émission, en lieu et place de l'histogramme du trafic, une jauge affichera la durée de passage en émission, par tranche de 60 secondes. 

À noter qu'à minuit, le nombre de passages en émission sur la journée, l'historique des 5 noeuds les plus actifs, ainsi que l'histogramme sont réinitialisés (à zéro).

### Ecran 128 x 128

En complément des informations visibles sur un écran 128 x 64 pixels, cette résolution permet d'afficher plus d'informations.

A ce titre, si aucune station n'est en émission, le RRFDisplay affichera :

* l'historique des 10 derniers noeuds étant passés en émission ainsi que l'horodatage,
* l'historique des 10 noeuds les plus actifs ainsi que la durée cumulée de passage en émission,
* l'état du Spotnik: architecture, uptime, noyau, charge et fréquence du CPU, température, adresse IP, occupation mémoire et disque, version,
* la configuration courante.

Si une station passe en émission, en lieu et place de l'histogramme du trafic, un compte à rebours affichera la durée de passage en émission. C'est plus lisible qu'une jauge.

Enfin, sur la partie basse de l'écran, figure un tableau listant l'activité sur les autres salons. A tout moment, il est donc possible de savoir s'il se passe quelque chose ailleurs. 

## Post installation sur Spotnik 3.0

### Installation de paquets complémentaires

En partant de la version 3.0 de Spotnik, commencez par cloner ce projet dans le répertoire /opt. Donc, depuis une connexion SSH, lancez les commandes suivantes:

`cd /opt`

Puis, 

`git clone https://github.com/armel/RRFDisplay.git`

Il faut également procéder à l'installation de quelques paquets complémentaires. Toujours depuis une connexion SSH, lancez les commandes suivantes:

`sudo apt-get update`

`sudo apt-get install i2c-tools libi2c-dev python-smbus python-pip python-dev python-pil python-lxml`

`sudo apt-get install libfreetype6-dev libjpeg-dev build-essential`

`sudo pip install --upgrade setuptools`

`sudo pip install requests`

`sudo pip install luma.oled luma.lcd`

`sudo pip install configparser`

Enfin, si ce n'est pas déjà fait, il reste à activer le support du protocole I2C afin de pouvoir dialoguer avec l'écran OLED. Ce sera l'étape la plus compliquée...

### Activation du support I2C sur Raspberry Pi

Utilisez l'utilitaire `raspi-config`. Une fois lancé,

* option 5 - Interfacing Options
* sous option P5 - I2C
* répondez oui ;)
 

### Activation du support I2C sur Orange Pi Zero

Utilisez l'utilitaire `armbian-config`. Une fois lancé,

* System
* Hardware
* Cochez i2c0
* Eventuellement, cochez i2c1
* Save

Rebootez.

Cochez i2c0 et i2c1 peut-être utile pour raccorder 2 écrans.

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

Le script `RRFDisplay.py` peut recevoir des arguments au lancement afin d'affiner les paramètres. Par exemple,

```
root@spotnik:/opt/RRFDisplay# python RRFDisplay.py -h
Usage: RRFDisplay.py [options ...]

--help               this help

Interface settings:
  --interface        set interface (default=i2c, choose between [i2c, spi])
  --i2c-port         set i2c port (default = 0)
  --i2c-address      set i2c address (default = 0x3C)

Display settings:
  --display          set display (default=sh1106, choose between [sh1106, ssd1306, ssd1327, ssd1351])
  --display-width    set display width (default = 128)
  --display-height   set display height (default = 64)
  --display-theme    set display theme (default=theme.cfg)

Follow settings:
  --follow           set room (default=RRF, choose between [RRF, TECHNIQUE, INTERNATIONAL, LOCAL, BAVARDAGE, FON]) or callsign to follow'
  
WGS84 settings:
  --latitude         set latitude (default=48.8483808, format WGS84)
  --longitude        set longitude (default=2.2704347, format WGS84)

Log settings:
  --log              enable log

88 & 73 from F4HWN Armel
```

Par défaut, sans argument, le RRFDisplay va démarrer avec les paramètres suivants,

- i2c port = 0
- i2c address = 0x3C
- display = sh1106
- display width = 128
- display height = 64
- display_theme = theme.cfg 
- follow = RRF
- latitude = 48.8483808
- longitude = 2.2704347  

À noter que latitude et longitude sont à paramétrer au format [WGS84](https://fr.wikipedia.org/wiki/WGS_84) (degrés décimaux) dans le fichier settings.py. 

Cela revient à lancer le RRFDisplay avec les arguments suivants,

`python /opt/RRFDisplay/RRFDisplay.py --i2c-port 0 --i2c-address 0x3C --display sh1106 --display-width 128 --display-height 64 --display_theme theme.cfg --follow RRF --latitude 48.8483808 --longitude 2.2704347`

Il est donc possible de modifier les paramètres, notamment en fonction de ce que vous retournera la commande `i2cdetect` décrite ci dessus.

Par exemple, avec les paramètres suivants,

- i2c port = 1
- i2c address = 0x3C
- display = ssd1306
- display width = 128
- display height = 64
- follow = TECHNIQUE

Il vous suffira de lancer le RRFDisplay avec les arguments suivants,

`python /opt/RRFDisplay/RRFDisplay.py --i2c-port 1 --display ssd1306 --follow TECHNIQUE`

Notez qu'il n'est pas nécessaire de préciser l'i2c-address, le display-width et display-height puisque ce sont déjà les valeurs par défaut. Idem pour la latitude et la longitude, qui par défaut sont les miennes...

Point important, il est aussi possible de préciser un indicatif de link à suivre, plutôt qu'un salon. Par exemple, si vous désirez suivre le F1ZPX, il suffit de préciser,

`python /opt/RRFDisplay/RRFDisplay.py --i2c-port 1 --display ssd1306 --follow F1ZPX`

Dès lors, le RRFDisplay affichera les informations du salon sur lequel se trouvre le link F1ZPX et le suivra automatiquement au grès de ses QSY.

Enfin, si vous voulez le laisser tourner en tache de fond, utilisez la commande `nohup` et l'_esperluette_ ;) Par exemple, 

`nohup python /opt/RRFDisplay/RRFDisplay.py --i2c-port 1 --display ssd1306 --follow TECHNIQUE &`

Et voilà ;)

## Script de démarrages

Je vous suggère de regarder les scripts de démarrages (fichier shell portant l'extension .sh) et des les adapater à vos besoins. Vous y trouverez des exemples en I2C et SPI.

## Liste des composants

Voici la liste des composants dont vous aurez besoin:

* 1 Raspberry Pi 3 ou 1 Orange Pi Zero
* 1 écran OLED 128 x 128 (1.5" type SSD1327 ou SSD1351) ou 128 x 64 (1.30" ou 0.96" type SH1106 ou SSD1306)
* 4 cables Dupont femelle / femelle

Il est possible d'adapter ce projet à d'autres platines et d'autres écrans. Ne pas hésitez à me contacter pour avis si vous le souhaitez ;)
 
## Augmenter la vitesse de transfert du bus I2C

Si vous utilisez un écran OLED 128 x 128 type SSD1327, vous aurez probablement à augmenter la vitesse de transfert du bus I2C. La résolution et le fait que cet écran fonctionne en niveau de gris impose une certaine bande passante afin d'avoir un FPS acceptable. 

Par chance, il est possible d'augmenter la vitesse du bus I2C sur un Orange PI Zero. Je n'ai pas testé sur Raspberry. 

Commencez par convertir le fichier `/boot/dtb/sun8i-h2-plus-orangepi-zero.dtb.dtb` en format .dts (format text éditable).

```
cd /boot/dtb
dtc -I dtb -O dts sun8i-h2-plus-orangepi-zero.dtb -o sun8i-h2-plus-orangepi-zero.dts
```

Editez le fichier .dts et ajouter une fréquence aux sections i2c0 (i2c@01c2ac00), i2c1 (i2c@01c2b000) et i2c2 (i2c@01c2b400). La valeur suivante correspond à 400 KHz (400 000 Hz).

```
clock-frequency = <0x61A80>; 
```

Et faites la convertion inverse.

```
dtc -I dts -O dtb sun8i-h2-plus-orangepi-zero.dts -o sun8i-h2-plus-orangepi-zero.dtb
```

Vous n'avez plus qu'à rebooter.

Au cas ou, dans le répertoire `tools/i2c` du projet, se trouve un script shell qui permet de faire cette modification. 


## Cablage I2C

### Raspberry PI 3

![alt text](https://github.com/armel/RRFDisplay/blob/master/doc/RRFDisplay_RPI.png)

### Orange PI Zero

![alt text](https://github.com/armel/RRFDisplay/blob/master/doc/RRFDisplay_OPI.png)

## Cablage SPI

| Ecran  |   Raspberry  | 
| ------ | ------------ | 
| VCC    |  +3.3V / +5V  | 
| GND    |   GND        |
| DIN    |   MOSI       | 
| CLK    |    SCK       | 
| CS     |    CE0       |
| DC     |    24 (BCM)   |
| RST    |    25 (BCM)   |
 

