# PyCommonist

PyCommonist est codé en Python/PyQt. Il est très largement inspiré de l'excellent logiciel [Commonist](https://commons.wikimedia.org/wiki/Commons:Commonist/fr). Il permet de téléverser facilement des photographies vers Wikimedia Commons.

Pour l'installer et le lancer (utilisation ici d'un environnement virtuel) :
* `git clone https://github.com/benprieur/PyCommonist.git`
* `cd PyCommonist`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `python3 main.py`

Au 26 janvier 2021, il a été testé sur MacOS et sur Linux Ubuntu. Ci-dessous une copie d'écran à cette date.

![Screenshot](img/screenshot0.png "Screenshot")

Dernières améliorations :

* 20 avril 2021 : ajout d'un fichier externe de configuration (largement inspiré par le code de User:Deansfa, merci à lui).
* 2 mai 2021 : ajout d'une auto-suggestion des catégories (idée de User:Romainbar, merci à lui).
* 12 mai 2021 : User:Romainbar
  * support des adresses copiées depuis OSM
  * si la case des catégories par défaut est vide, la ligne n'est pas créée dans la page
  * ajout du code langue pour la description
* 14 mai 2021 : User:Romainbar
  * bouton pour modifier l'ordre de tri des images, entre nom de fichier (par défaut) et date Exif
  * transformation des cases à cocher en boutons pour les images à importer, et déplacement dans la frame de droite
  * case à cocher Import automatiquement à True quand on modifie le nom de l'image
* 31 mai 2021 : User:Romainbar
  * affichage du bon total des uploads réussis et ratés
* 2 juin 2021 : User:Romainbar
  * bouton pour recharger la liste des images à partir du dernier dossier sélectionné
* 12 juin 2021 : User:Romainbar
  * bouton pour copier et coller les nom, description et catégories d'une image à l'autre
  * possibilité d'incrémenter automatiquement le dernier numéro contenu dans le nom
* 13 juin 2021 : User:Romainbar
  * dialogue de confirmation d'upload quand aucune description ou aucune catégorie n'est entrée

