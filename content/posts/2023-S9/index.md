---
title: "Episode 2: résoudre une tâche d'Aspect Based Sentiment Analysis - Analyse exploratoire"
date: 2023-03-21T09:03:36+01:00
draft: true
resources:
- name: config_1
  src: config_1.vg.json
- name: config_2
  src: config_2.vg.json
- name: sample_data 
  src: sample_data.csv
---

Après deux bonnes semaines de pause ~~passées à se prélasser au bord d'une piscine d'un hôtel 5 étoiles aux Bahamas~~, 
nous pouvons enfin reprendre les choses sérieuses. 


Au menu d'aujourd'hui, nous allons effectuer une première analyse exploratoire. L'objectif?

Rien de sorcier, à savoir déterminer quelques statistiques basiques sur les topics. Enfin je ne vous spoile pas tout 
tout de suite...


Tout le travail qui suit a été effectué dans un environnement _jupyter_.


## C'est parti

Pour cette étude nous n'avons besoin que de deux librairie: _pandas_ (pour charger les données et calculer des stats), puis _altair_ 
(pour la data-viz). Définissons le chemin vers les données d'entraînement.

```python
import pandas as pd
import altair as alt

TRAIN_PATH = "SemEval2017-task4-dev.subtask-BD.english.INPUT.txt"
```

A quoi ressemblent les données?

```python
data = pd.read_csv(train_path, sep="\t", header=None)
data.head()
```

{{< figure src="image_1.png"  width="600">}}

Passons rapidement sur le préprocessing initial, qui nous permet d'obtenir les données suivantes:

{{< figure src="image_2.png"  width="600">}}

Comme lorsque l'on fait ses courses, on se pose en premier lieu une liste de questions:
- Combien de topics y-a-t-il? Est-ce que certains se ressemblent?
- Apparaissent-t-il de façon explicite dans chaque tweet? 
- Y-a-t-il des cas de tweets multi-topics?
- Combien y a-t-il d'exemples de chaque classe (positif/négatif) au global? et pour chaque topic?
- Les tweets partagent-ils des caractéristiques communes, ont-ils quelque chose de particulier?


**Nombre et nature des topics**

````python
>>> topics = data["topic"].unique()
>>> len(topics)
>>> 100
>>> topics
>>> array(['amy schumer', 'ant-man', 'bad blood', 'bee gees', 'big brother',
       'boko haram', 'briana', 'brock lesnar', 'caitlyn jenner',
       'calibraska', 'carly fiorina', 'cate blanchett', 'charlie hebdo',
       'chris evans', 'christians', 'chuck norris', 'curtis',
       'dana white', 'dark souls', 'david bowie', 'david price',
       'david wright', 'dean ambrose', 'dunkin', 'dustin johnson',
       'ed sheeran', 'eid', 'floyd mayweather', 'foo fighters',
       'frank gifford', 'frank ocean', 'gay', 'george harrison',
       'george osborne', 'gucci', 'hulk hogan', 'ice cube', 'ira', 'iran',
       'iron maiden', 'islam', 'israel', 'janet jackson', 'jason aldean',
       'john cena', 'john kasich', 'josh hamilton', 'justin bieber',
       'kane', 'kanye west', 'katy perry', 'kendrick', 'kendrick lamar',
       'kim kardashian', 'kpop', 'kris bryant', 'lady gaga', 'milan',
       'miss usa', 'moto g', 'murray', 'muslims', 'naruto',
       'national hot dog day', 'national ice cream day', 'niall', 'nicki',
       'nirvana', 'paper towns', 'paul dunne', 'paul mccartney',
       'prince george', 'ps4', 'rahul gandhi', 'randy orton',
       'real madrid', 'red sox', 'rolling stone', 'rousey', 'ryan braun',
       'sam smith', 'saudi arabia', 'scott walker', 'seth rollins',
       'sharknado', 'shawn', 'star wars day', 'super eagles', 'the vamps',
       'thor', 'tom brady', 'tony blair', 'twilight', 'u2', 'watchman',
       'white sox', 'yakub', 'yoga', 'zac brown band', 'zayn'],
      dtype=object)
````


- On dénombre 100 topics
- Plusieurs catégories de topics sont concernées: 
  - Des personnalités réelles ou fictives (Amy Schumer, Naruto...)
  - Des groupes de musique (Bee gees, Foo fighters ...)
  - Des thèmes de société et de religion (gay, islam, christians)
  - Des inclassables (Star wars day, Moto g, PS4...)
- Deux topics partagent le même sujet: islam & muslims

**Les topics sont-ils explicites?**

````python
>>> data.apply(lambda row: row.topic in row.tweet_text.lower(), axis=1).sum() / len(data)
>>> 0.9997
````

- Oui, dans 99,9% des tweets on retrouve le topic dans le texte (ce dernier mis en _lowercase_). Déterminer le topic 
n'est donc pas un défi.

**Y-a-t-il des cas de tweets multi-topics?**

````python
>>> (data.groupby("tweet_id").topic.count() > 1).sum()
>>> 16
````

- Très peu (16 pour 10k tweets environ)

**Combien y a-t-il d'exemples de chaque classe (positif/négatif) au global? et pour chaque topic?**

**a. Global**
```python
aggregated_data = data.groupby("polarity", as_index=False).tweet_id.count()

count_positive = aggregated_data.loc[aggregated_data.polarity == "positive", "tweet_id"].values[0]
count_negative = aggregated_data.loc[aggregated_data.polarity == "negative", "tweet_id"].values[0]

alt.Chart(
    aggregated_data, 
    title=f"Negative to positive class ratio: {count_negative / count_positive:.2f}"
).encode(
    x=alt.X("tweet_id:Q", title="Count of records"),
    color=alt.Color("polarity:N", scale=alt.Scale(range=["red", "green"]), title="Polarity", legend=None), 
    row=alt.Row("polarity:N", title="Polarity"), 
    tooltip=[alt.Tooltip("tweet_id:Q", title="Count"), alt.Tooltip("polarity:N", title="Polarity")]
).mark_bar()
```
Au global, voici la répartition de la polarité (_figure interactive_):

{{< vega file="config_2" div_id="config_2" >}}

On observe une tendance déséquilibrée de la polarité en faveur de la classe positive, le nombre de tweets négatif étant 
environ de 30% le nombre de tweets positifs. 

**b. Topic**

````python
alt.Chart(
    data.groupby(["topic", "polarity"], as_index=False).tweet_id.count(), 
    title=alt.TitleParams(
      f"Tweet count by polarity for the {data.topic.nunique()} topics in the dataset", 
      anchor="start"
    )
).encode(
    x=alt.X("topic:N", title="Topic", sort="-y"), 
    y=alt.Y("tweet_id:Q", title="Tweet count", stack=True), 
    color=alt.Color("polarity:N", scale=alt.Scale(range=["red", "green"]), title="Polarity"), 
    tooltip=[alt.Tooltip("tweet_id", title="Count"), "topic:N"]
).mark_bar(
    opacity=0.7
)
````


Augmentons la granularité de ces résultats en affichant les statistiques pour chaque topic:
> 💡C'est une carte interactive, survolez-là avec le curseur et scrollez pour voir l'intégralité des résultats 

{{< vega file="config_1" div_id="config_1" >}}

On constate que selon les topics, la répartition positive/négative de la polarité est très variable. On retrouve 
notemment:
- Des sujets faisant la quasi-unanimité en positif (ex. foo fighters) ou en négatif (ex boko haram)
- Des sujets équilibrés (ex. kanye west)
- Des sujets à parti pris en positif ou négatif, mais pas totalement déséquilibrés (ex. seth rollins)

On remarque également que le nombre de tweets par topic est très variable, qu'il peut aller de 25 à 231. On a donc de 
grandes disparités de classes.

**Les tweets partagent-ils des caractéristiques communes, ont-ils quelque chose de particulier?**
- Prenons un échantillon de 0,5% des données (environ 50 lignes). On obtient la table suivante:

{{< csv-table file="sample_data" >}}

On remarque les choses suivantes dans cet extrait:
- Présence de nombreuses URL
- Encodage de l'amperande (`&amp`) et de smileys (`:-/`). On remarquera d'autres smileys dans le dataset entier.
- Hashtags (`#<sujet>`), références (`@<pseudo_twitter>`)
- Abbréviation ("R" -> "?", "2gether" -> "together")
- Polarité positive malgré des tournures de phrases négatives (_"Could not be happier"_)
- Labelling contestable: _"@EchoOfIndia Also, his anger against Hindus are justified but couldn't get why he was so anti 
Islam..may be he was just fed up of religions"_ est considéré négatif envers le topic "islam", alors que l'auteur du
tweet se demande pourquoi une certaine personne serait contre cette religion


## Et pour la suite?
Je ne sais pas vous, mais jusqu'ici je suis assez satisfait de la compéhension du jeu de données:
- On sait qu'on fait face à un bon déséquilibre de classes, tant dans les topics que dans la polarité
- Que pour l'écrasante majorité des cas, on a un seul topic concerné par tweet
- Le contenu textuel des tweets est sans doute à nettoyer pour virer les URL; pour remplacer les smileys et caractères 
encodés bizarrement; il y aura peut-être un travail à faire sur les hashtags ainsi que les références

Dans le prochain article, on se chargera de créer un premier modèle en faisant quelques larges hypothèses, avec pour 
idée de mettre en place la chaîne de pré-traitement / modélisation / évaluation de bout en bout.

Stay tuned!


