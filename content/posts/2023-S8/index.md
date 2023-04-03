---
title: "Episode 1: résoudre une tâche d'Aspect Based Sentiment Analysis - Préliminaires"
date: 2023-03-06T17:07:53+01:00
draft: false
tags: ["data science", "sentiment analysis", "absa"]
summary: "Dans cette série, nous allons tenter de résoudre un problème d'analyse de sentiments, en nous basant sur des 
jeux de données de référence et des techniques de l'état de l'art."
---
# 📂 Episodes précédents

_Sur la même thématique_:
- {{< page_link path="/posts/2023-S6" >}}
- {{< page_link path="/posts/2023-S7" >}}

Série _résoudre une tâche d'Aspect Based Sentiment Analysis_:
- **{{< page_link path="/posts/2023-S8" >}}**

# 📝 Mise en contexte
Là, on en a marre. Théorie par-ci, explications fumeuses par là; quand est-ce qu'on pratique?

Et bien Marcel mets ta ceinture, parce qu'on va se lancer dans une grande aventure: celle de résoudre une tâche 
d'_Aspect Based Sentiment Analysis_ (ABSA).

Laquelle? Et bien comme on a été curieux, on sait désormais qu'il y a plusieurs challenges phares dans ce domaine: 
c'est les évènements _SemEval-20XX_ (pour _Semantic Evaluation_), déclinés en plusieurs millésimes de 2014 à 2017. 

Ceux qui se croient malin feront la remarque qu'il en existe d'autres jusque 2023 (et oui, on en fait une cuvée par an), 
mais je leur rappelerai que les tâches de ces challenges ne sont pas en lien avec l'ABSA.

Comme on aime la modernité, on va s'intéresser seulement au petit dernier, le **SemEval-2017**. 




# ⚙️ Mise en place de l'environnement

**C'est quoi ce  challenge? Qu'est-ce qu'on va y faire?**

Alors c'est très simple. Le challenge SemEval, c'est un évènement qui propose une liste de sujets centrés sur la 
thématique d'évaluation sémantique, aka. dire des choses sur du texte. Il y a plusieurs sujets, et dans chaque sujets on 
retrouve des sous-problèmes. Chaque sujet est grosso-modo un problème général (par exemple _Sentiment Analysis in 
Twitter_), et chaque sous-problème aborde une facette du sujet. 


Alors direction le [site internet](https://alt.qcri.org/semeval2017/index.php?id=tasks) du challenge, regardons les 
problèmes à résoudre associés à:


{{< figure src="figure_1.png"  width="400">}}

Dans notre cas particulier, on a l'embarras du choix:
- Message Polarity Classification: Given a message, classify whether the message is of positive, negative, or neutral 
sentiment.
- Topic-Based Message Polarity Classification [...]
- Tweet quantification: Given a set of tweets about a given topic, estimate the distribution of the tweets [...]

Comme nous nous intéressons avant-tout aux problèmes d'_ABSA_, prenons le parti de choisir le second challenge, décrit 
ci-dessous:

![figure_2](figure_2.png)

Lançons nous sur cette tâche, téléchargeons les données et c'est parti!

# 🛢 Les données


On remarque cinq fichiers dans l'archive de données

{{<figure src="figure_3.png" height="150">}} 
En y jetant un oeil et en lisant le README on se rend compte que:
- **baseline-B-english.txt** est un fichier regroupant les prédictions de la méthode baseline, on y 
voit 3 colonnes: identifiant de tweet, topic et polarité  
- **SemEval2017-task4-dev.subtask-BD.english.INPUT.txt** est le dataset _train_, on y retrouve les mêmes colonnes ainsi 
qu'une de plus, contenant le texte des tweets
- **twitter-2016test-BD-English.txt** se fait appeler le "GOLD file", et qui est en fait un copier-coller du dataset de 
train, sans la dernière colonne. On a juste les vérités terrains quoi ⚠️En revanche, il s'agit des résultats de... 2016, 
donc on s'en fiche
- **SemEval2017_task4_test_scorer_subtaskB.pl** est un script `perl` permettant de calculer les métriques du challenge 
à partir de prédictions. Celles-ci sont: _macro-average Recall_, _macro-average F1_, et _Accuracy_

**Remarques**
- D'après le [compte rendu](https://aclanthology.org/S16-1002.pdf) du challenge de l'année précédente, la méthode baseline 
est le classifier qui attribue à chaque tweet une polarité positive.
- Le macro-averaged est défini de façon particulière, puisqu'il ne s'agit pas d'un recall classique. Suit la formulation 
du recall:
  - \\( R_{topic} = \frac{1}{2}( R_{topic, N} + R_{topic, P}) \\) avec \\( R_{topic, X} \\) le rappel pour le topic et 
la polarité X
  - \\( R = \frac{1}{N} \sum_{topic} R_{topic} \\)




_Un exemple du dataset d'entraînement:_
{{<figure src="figure_5.png">}}

# 📊 Evaluation

Première chose à faire, vérifions que le script d'évaluation fonctionne:

```shell
perl SemEval2017_task4_test_scorer_subtaskB.pl \
  SemEval2017-task4-dev.subtask-BD.english.INPUT.txt \  # PREDICTION
  SemEval2017-task4-dev.subtask-BD.english.INPUT.txt  # VERITE TERRAIN
```

On obtient les résultats suivants:

![figure_4](figure_4.png)

Et un fichier .scored est créé avec les métriques en question:
````text
	positive: P=1.0000, R=1.0000, F1=1.0000
	negative: P=1.0000, R=1.0000, F1=1.0000
		AvgF1_2=1.000, AvgR_3=1.000, Acc=1.000
	OVERALL SCORE : 1.000
````

Tout est loggé, les métriques sont au max, donc top on peut continuer.

Que donne la baseline en revanche? Effectuons le même test par la commande suivante:

````shell
perl SemEval2017_task4_test_scorer_subtaskB.pl \
  baseline-B-english.txt \                            
  SemEval2017-task4-dev.subtask-BD.english.INPUT.txt

````

On obtient ces résultats:
````text
	positive: P=1.0000, R=0.7783, F1=0.8753
	negative: P=0.0000, R=0.0000, F1=0.0000
		AvgF1_2=0.438, AvgR_3=0.389, Acc=0.778
	OVERALL SCORE : 0.438
````

Hum, notre baseline fonctionne bien pour prédire les polarités positives (il a un bon F1), mais il se gauffre 
complètement en prédisant des classes négatives.


# 🗓 Et ensuite

Quoi, c'est déjà fini?

Eh oui, on avance doucement mais sûrement, ce serait dommage de se cramer les ailes en si bon chemin non?

Au prochain épisode, on ira charger les données avec python 🐍, jouer un peu avec et ~~avec de la chance~~, on obtiendra 
des premiers résultats; j'ai hâte de vous les montrer!  

Allez, à la semaine prochaine!

---

