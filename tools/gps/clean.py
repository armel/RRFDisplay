#!/usr/bin/env python3

'''
Clean tools
2to3 -w -x apply clean.py
'''

import time

def main():

    start = time.time()

    # Lecture du fichier de donnees

    data = [line.strip() for line in open('wgs84.dat')]

    # Boucle principale

    link = []

    for l in data:
        l = l.split(' ')
        if l[0] in link:
            print(l)
        else:
            link.append(l[0])

    print(link)

    # Affichage du resultat

    print("Temps d'execution : %.1f secondes" % (time.time() - start))

if __name__ == '__main__':
    main()