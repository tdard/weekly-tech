---
title: "«Mais comment je résous ce problème moi?!» Modélisation en analyse de sentiment basée sur l'aspect"
date: 2023-02-21T09:08:36+01:00
draft: true
tags: ["data science", "sentiment analysis", "absa"]
---

Dans cet article nous allons parler de modélisation, ou comment aborder un problème en analyse de sentiment basée sur 
l'aspect.

# Mise en situation
Lundi 27 février 2023, 10:05. 

Votre ami Eustache vient de vous parler d'une n-ième compétition Kaggle, dont le prix dépasse de très loin votre bonus 
annuel de trois malabars et 5 points d'inflation. 

Alors en plein travail -mais la fin justifiant les moyens-, vous laissez tout en plan pour vous connecter illico sur 
votre compte, pour voir de quoi il en ressort. 

La langue pendante après avoir observé de vos propres yeux la récompense affichée, vous commencez à lire le sujet afin 
de comprendre ce qui vous est demandé. Il est écrit des termes bizarres comme "topics", "sentiments", "opinion" et peu à 
peu, votre regard devient blême et votre teint se jaunit. Votre coeur devient lourd et c'est alors que vous vous écriez 
en plein open-space: 

_«Mais comment je résous ce problème moi?!»_

Pris de panique en remarquant les nuages sombres au dessus de la tête de votre manager, vous vous excusez d'un ton las 
puis vous vous remettez à penser. Par un éclair de génie (et parce que vous avez lu l'[article précédent](/weekly-tech/posts/2023-s6) bien sûr), vous réalisez d'un coup qu'il s'agit d'une tâche d'analyse de 
sentiment basée sur l'aspect: vous devez prédire simultanément les topics avec leur polarité dans chaque texte de la 
base de donnée présentée.

Votre sang se glace alors davantage, puisque vous ne savez pas du tout comment vous y prendre. 

{{< center >}}
![image_1](image_1.jpeg)
{{< /center >}}
Heureusement pour vous, vous décidez d'aller voir sur [weekly-tech.io](https://weekly-tech.io) pour voir si un article 
peut répondre à votre seconde question: 

_"Sur quoi vais-je pouvoir faire fit predict?"_

Par chance, c'est ce dont on va parler aujourd'hui.

# Modélisation
L'étape de modélisation permet de définir l'allure des entrées-sorties d'un modèle prédictif.
Dans le cas de l'analyse de sentiment basée sur l'aspect, on peut dénombrer 4+1 paradigmes:
- _Sequence-level Classification (SeqClass)_
- _Token-level Classification (TokenClass)_
- _Machine Reading Comprehension (MRC)_
- _Sequence-to-Sequence (Seq2Seq)_

Ajouté à ces quatres familles de modélisation, on compte également un méta-paradigme: les méthodes dîtes 
_Pipeline_.

## Sequence-level Classification

On considère un texte d'entrée \\(X\\), et on cherche à prédire une (ou plusieurs) classes parmi M (connu) possibles. 
La sortie est donc un vecteur de taille M, one ou multi-hot.

Ce paradigme de modélisation fait intervenir un encodeur (noté \\(Enc\\)) permettant d'extraire des descripteurs de la 
phrase, et un classifieur (noté \\(CLS\\)) exploitant ces derniers afin de prédire les classes désirées.


> Formulation: \\(Y = CLS(Enc(X))\\)


En jouant avec la _nature_ des classes, on peut peut résoudre des problèmes composés:
- Si on considère autant de classes que de catégories d'aspect à prédire, on reste dans des tâches simples
- Si on considère autant de classes que de polarités PAR catégorie d'aspect, on peut ainsi réaliser -par exemple -
l'extraction jointe des topics et de leur polarité 

> Cette façon de faire est prénommée _AddOneDim_, elle est l'objet du papier de recherche [“Joint aspect and polarity 
classification for aspect based sentiment analysis with end-to-end neural networks](https://arxiv.org/abs/1808.09238)  


## Token-level Classification

On considère un texte d'entrée \\(X\\) composé de N tokens, et on cherche à prédire une (ou plusieurs) classes parmi M 
possibles, ce pour chaque token. 

La sortie a donc la même longueur que l'entrée, elle est une matrice \\((N, M)\\).

En reprenant des descripteurs encodés (de façon similaire au paradigme _SeqClass_), on va cette fois-ci appliquer un 
décodeur (noté \\(Dec\\)) pour retrouver en sortie la dimension initiale du texte.

> Formulation: \\(Y = Dec(Enc(X))\\) avec \\(dim(Y) = dim(X)\\)

Cette modélisation est très puissante, car elle dispose d'une fine granularité sur la prédiction: chaque token peut être 
qualifié plusieurs termes de sentiments à la fois (aspect, opinon, catégorie ou polarité).

## Machine Reading Comprehension


Le MRC consiste à poser une question à un modèle tout en lui indiquant dans quel texte chercher. Ce dernier retourne une 
réponse, qui peut prendre bien des formes:
- Une phrase bien formulée (comme vous pouvez voir en utilisant ChatGPT)
- Le passage dans le texte qui correspond à la localisation de l'information cherchée.
  - Pour ceci, on peut retourner les bornes de début et de fin du paragraphe

Dans ce second cas, on encode une question \\(X_q\\) et un texte associé \\(X\\), pour enfin le classifier:

> Formulation: \\(y_s, y_e = CLS(Enc(X, X_q))\\)


## Sequence-to-Sequence

Dans le paradigme Seq2Seq, le modèle ingère une phrase en entrée puis il en renvoie une en sortie. Cette technique est 
similaire aux paradigmes SeqClass et TokenClass, mais il s'en différencie en ne contraignant pas la longueur de la 
réponse.

> Formulation: \\(Y = Dec(Enc(X))\\)



## Pipeline

Les techniques de pipelining sont des méta-techiques: elles utilisent la composition de plusieurs techniques de façon 
séquentielle pour résoudre un problème.

On pourrait ainsi implémenter un algorithme détectant les catégories d'aspect et la polarité associée en deux temps:
1. Détecter les catégories d'aspect dans le texte (avec par exemple une méthode _SeqClass_)
2. Puis déterminer la polarité associée pour chacune (avec une méthode _MRC_)


La littérature semble indiquer que ces techniques sont peu performantes, car elles souffrent de l'accumulation 
d'erreurs. En effet, comme chaque tronçon du _pipeline_ est _conditionné_ par les tronçons précédents, les erreurs se 
propagent de niveau en niveau

> En reprenant l'exemple précédent, si le modèle se trompe dans les catégories détectées, la détermination de la 
> polarité sera désuette


# Métriques

Le problème -direz-vous- lorsque l'on est en ABSA, est de déterminer la qualité d'une prédiction. En effet, le modèle 
est amené à prédire la présence (ou absence) de **plusieurs** éléments porteurs de sentiments:
- Que dire d'une prédiction faisant état d'une polarité correcte et d'une fausse?
- Que dire d'une prédiction faisant état d'un terme d'aspect correct mais d'un mauvais terme d'opinion associé?

Pour résoudre ce problème, la solution (en général) apportée ne fait pas dans la finesse, il s'agit de dire:
> La prédiction est vraie, seulement si tous ses éléments prédits sont corrects

Pas de demi-mesure, on a tout-vrai ou faux. On appelle cette technique l'**Exact Matching**


Pour l'aspect métriques, on reste sur du nominal en tâches de classification avec la ~~sainte~~ trinité F1, précision et 
rappel. 


# Composantes d'architecture

Dans cet article, nous avons abordé les notions de classifieur, d'encodeur et de décodeur. Quelles techniques peuvent 
convenir à quoi?


## Encodeurs
Manifestement il y a une diversité dans les approches d'encodage; on y retrouve: 
- Réseaux de neurones convolutifs 
- Réseaux de neurones récurrents
- Transformers

Bien qu'il s'agisse là un méli-mélo de techniques, il semble que l'approche _transformers_ soit la plus prometteuse.


- Il ne faut pas oublier que chaque approche d'encodage vient accompagnée d'une représentation vectorielle des entrées 
qu'on appelle **prolongement lexicaux** (ou word embeddings en anglais). 
- Les techniques les plus courantes sont appelées Word2Vec et GloVe (vous pourrez utiliser ces embeddings avec des libs 
python, par exemple [gensim](https://pypi.org/project/gensim/))

Si vous voulez utiliser des réseaux convolutifs ou récurrents, vous _devrez_ appliquer **manuellement** ces 
transformations d'embeddings sur le texte avant de nourrir le modèle, tandis que les approches de transformers (type 
BERT) viennent accompagnées de leur propre prolongement lexical.

## Classifieurs et décodeurs

Les classifiers et décodeurs sont généralement la partie la moins complexe de l'architecture d'un modèle. On y retrouve 
dans les grandes lignes des **perceptrons multi-couches** accompagnés d'une couche de **pooling**, de softmax ou de 
sigmoïde. Eventuellement, on peut retrouver des CRF (conditional random fields, de la famille des modèles probabilistes)


## Vers quoi s'orienter?

Tout ce qu'on a vu est très beau, on comprend qu'il y a plusieurs familles de techniques, dont on est capable de 
décrire à peu de chose près les composants. 

C'est très bien pour comprendre, mais c'est encore mieux de partir de travaux existant.

Pour comprendre quelles techniques ont déjà été éprouvées, je vous recommande de vous fier à la table ci-dessous tirée 
du papier de recherche [A Survey on Aspect-Based Sentiment Analysis:
Tasks, Methods, and Challenges](https://arxiv.org/pdf/2203.01054.pdf) (papier sur la base duquel cet article et le 
précédent ont été écrits) qui résume le champ des possibilités:

{{< center >}}
![image_2](image_2.png)
{{</ center >}}



