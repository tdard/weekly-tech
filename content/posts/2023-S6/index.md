---
title: "'La pizza était délicieuse mais le service était déplorable: genèse de l'aspect based sentiment analysis'"
date: 2023-02-15T21:34:06+01:00
draft: true
---

Cet article a pour ambition d'introduire de façon très superficielle la notion _d'analyse de sentiment basée sur 
l'aspect_ (ou _Aspect Based Sentiment Analysis_, ABSA en anglais).

Dans un premier temps, l'article se veut de présenter dans quel contexte ce champ de recherche est né, puis de donner 
quelques clés de vocabulaire, et enfin d'introduire aux grandes classes de problèmes que l'on peut rencontrer.

Cet article est le premier d'une série de 3 ou 4, il se veut très court. Le prochain concernera les paradigmes de 
modélisation, et leur application aux modèles de langages pré-entraînés (type BERT et compagnie).

Bonne lecture.


## Naissance de l'_aspect based sentiment analysis_
Depuis la nuit des temps, l'Homme a voulu savoir ce qu'on pensait de lui, ainsi que de ce qui lui était associé. 

Qu'il soit question de son apparence physique, de ses possessions matérielles ou de ses idées, il a toujours compté pour 
lui d'avoir un retour des autres.

Les marchands de biens et de services ne font pas exception à cette règle universelle: en observant et analysant ce que 
les gens disent de leurs produits et de leur entreprise, ils peuvent ainsi s'adapter et prospérer dans leur activité.

Néanmoins, s'il n'est pas difficile pour le vendeur de bettraves du marché de Flavigny-sur-Ozerain de comprendre 
l'opinion de ses clients -qui doivent se compter sur les doigts d'une demi-main-, il est beaucoup plus compliqué pour de 
**grosses** entreprises d'analyser manuellement (_exception faite de [ceux qui emploient des Kenyans à 2 dollars de l'heure](https://time.com/6247678/openai-chatgpt-kenya-workers/)_) toute 
une base de commentaires - qui peut en compter des dizaines de milliers. 

{{< center >}}
![meme_1](meme_1.jpeg)
{{< /center >}}

Pour leur plus grand bonheur, des scientifiques bien cartésiens se sont appropriés le problème et ont créé un champ de 
recherche entier dédié à cette cause, un oxymore du nom d'**analyse de sentiment**.

Comme ces informaticiens pensent en binaire (à quoi vous attendiez-vous?), les méthodes traditionnelles font l'hypothèse 
que chaque texte peut prendre deux "couleurs" (et éventuellement des nuances de gris entre les deux): positif, et 
négatif.

> A la phrase "La pizza est délicieuse!", on va pouvoir indiquer que le texte est positif. 

Manque de chance, ces approches montrent leur limite lorsqu'il y a plusieurs sujets (appelés _aspects_) considérés 
par une opinion. La phrase suivante est-elle positive ou négative si on considère qu'elle peut seulement être bonne ou 
mauvaise?

> "La pizza était délicieuse mais le service était déplorable"

En une seconde, vous comprenez qu'elle est positive ET négative à la fois, mais pas sur le même aspect.
Pour répondre au besoin de détecter l'expression des sentiments à travers plusieurs aspects, a émergé un domaine 
nouveau: l'_aspect based sentiment analysis_ ou analyse de sentiment basée sur l'aspect.

## Analyse de sentiment basée sur l'aspect: un peu de vocabulaire

### Taxonomie

Pour introduire de façon convenable ce champ de recherche, il faut définir une base commune de vocabulaire. 
Heureusement pour vous, il n'y a que quatre termes principaux à retenir pour l'instant; ceux-ci sont les éléments 
porteurs de sentiment dans un texte.

> "La pizza était délicieuse!"

- Le terme d'aspect
  - C'est le terme sur lequel est porté un sentiment (ici: "pizza")
  - Il est parfois implicite (par exemple dans la phrase: "C'est beaucoup trop cher!")
- La catégorie d'aspect
  - La catégorie englobe un ensemble de termes d'aspects. Par exemple, "pizza" pourrait appartenir à la catégorie 
"nourriture"
- L'opinion
  - Il s'agit du terme exprimant le sentiment. Ici, il s'agit de "délicieuse"
- La polarité
  - Indique si le jugement porté est positif ou négatif (ici, positif)


### Types de problèmes

On peut trier les problèmes d'ABSA en deux catégories distinctes, qu'on appelera _simples_, et _composés_.

- Un problème **unique** (_Single ABSA_ en anglais) consiste à trouver un unique type d'éléments dans du texte, ou bien plusieurs, mais sans 
relations entre eux. On parle alors de _co-extractions_
- Un problème **composé** (_Compound ABSA_ en anglais) consiste à trouver plusieurs types d'éléments dans du texte, en relation les uns avec les 
autres 

Voyons un exemple pour cerner la différence entre un problème composé et un de co-extraction de termes d'aspects et 
d'opinion:


> co-extraction("La pizza était délicieuse mais le service était déplorable", {termes d'aspect, termes d'opinion}) = {pizza, service}, {délicieuse, déplorable}

Par la co-extraction, on retourne l'ensemble des termes d'aspects et d'opinion, mais on ne sait quel terme d'opinion est 
associé au terme d'aspect.

> Compound("La pizza était délicieuse mais le service était déplorable", {termes d'aspect, termes d'opinion}) = {pizza, délicieuse}, {service, déplorable}

L'approche _compound_ analyse les relations entre les termes de sentiments, et permet ainsi de savoir quel terme 
d'aspect est associé à quel terme d'opinion. 


## En bref

- Les techniques d'analyse de sentiment sont là pour aider à résumer un grand volume d'avis qui ne pourrait pas être 
traité par un être humain de façon efficace
- Pour des tâches simples telles que "dis moi si ce commentaire est positif ou négatif", les techniques traditionnelles 
d'analyse de sentiment sont adaptées
- En revanche, lorsqu'il y a besoin d'analyser chaque commentaire sous plusieurs angles, les méthodes classiques ne 
sont pas adaptées et il faut se pencher vers l'application de techniques d'analyse de sentiment basées sur l'aspect
- On dénombre 4 éléments porteurs de sentiments dans ce cadre là: le terme d'aspect,sa catégorie, l'opnion porté et la 
polarité
- Il y a deux grandes familles de problèmes en ABSA: _single_, et _compound ABSA_. Cette dernière permet d'obtenir 
plusieurs éléments porteurs de sentiment avec leurs relations


---