---
title: "Episode 3: résoudre une tâche d'Aspect Based Sentiment Analysis - Modélisation"
date: 2023-03-29T09:44:40+02:00
draft: true
tags: ["data science", "sentiment analysis", "absa"]
resources:
- name: spec_1
  src: spec_1.vg.json
---

## 📂 Episodes précédents

_Sur la même thématique_:
- {{< page_link path="/posts/2023-S6" >}}
- {{< page_link path="/posts/2023-S7" >}}

Série _résoudre une tâche d'Aspect Based Sentiment Analysis_:
- {{< page_link path="/posts/2023-S8" >}}
- {{< page_link path="/posts/2023-S9" >}}
- **{{< page_link path="/posts/2023-S10" >}}**


## Introduction

Alors, me revoila assez vite pour vous présenter la modélisation qui suit l'analyse exploratoire effectuée précédemment.

Au risque de déplaire à certains, nous allons commencer sobrement avec des méthodes très classiques.

Pourquoi donc? Pour la bonne raison qu'on ne se débarasse pas d'un moustique avec un hélicoptère d'attaque; on commence 
par tenter de le zigouiller avec ses mains, avant de se laisser tenter par la tapette, la raquette 
électrique, le napalm ou le bazooka pour les plus haîneux d'entre nous.

Ici c'est pareil, notre pipeline _scikit-learn_ simple et basique sera facile à mettre en place, et on va pouvoir 
vérifier rapidement là où il est mauvais. Cela nous permettra de passer à l'étape suivante, en tentant de palier à ses 
limites.



## 🔧Choix de modélisation

On a pu voir dans un article précédent les différents paradigmes de modélisation, ici nous allons tenter une approche 
_SeqClass_ (classification de phrase) dont les features seront calculées sur une base de _bag-of-words_.

> C'est quoi un _bag-of-words_? Eh bien Jamy, un _sac de mots_ c'est une représentation vectorielle d'un texte (ici un 
> _tweet_), où chaque élément correspond à un _token_ de ton vocabulaire et la valeur associée à cet élément vaut 0 si 
> le _token_ n'apparaît pas dans le texte, et 1 sinon.

Notre modélisation restera classique (pour l'instant 👀):
- _Bag-of-words_ supplémenté par du _TF-IDF_ 
- Régression Logistique 

Pour cela on effectue deux hypothèses fortes:
- La présence de certains mots est l'unique facteur déterminant de la polarité
- Comme on a moins de 1% des tweets concernant plusieurs topics, on ne prendra pas en compte le topic dans les features 
de notre modèle

On fera attention à quelques détails néanmoins, pour gérer l'_imbalance_ du _dataset_ concernant le nombre de tweets à 
polarité négative par rapport aux positifs.

> C'est quoi le TF-IDF? En bref, un mot est considéré important: (1) quand il apparaît dans peu de documents; (2) quand 
> il apparaît de nombreuses fois dans un même document

## 🚀 Let's code

Tel Machiavel, préméditons notre méfait en planifiant. Pour **entraîner un modèle et analyser ses résultats**, il nous 
faut:
1. Charger les données dans un format convenable
2. Diviser celles-ci en un jeu d'entraînement et un de validation (disons que l'on s'en fiche d'en avoir un 3è de test 
comme on reste très simple)
3. Instancier le modèle, puis l'entraîner
4. Calculer des métriques pour nous informer sur la qualité des résultats
5. Sauvegarder les prédictions fausses quelque part pour les analyser individuellement



### Préparation des données

Comme nous ne sommes pas des cochons mais que nous développons notre modèle dans un notebook (oxymore), nous mettrons en 
place des fonctions utilitaires pour rendre notre code plus clean.

_utils.py_
````python
import pandas as pd

def load_data(path: str) -> pd.DataFrame: 
    data = pd.read_csv(path, sep="\t", header=None)
    data = data.drop(columns=[4])
    data = data.rename(columns={0: "tweet_id", 1: "topic", 2: "polarity", 3: "tweet_text"})
    return data
````

_notebook.ipynb_
```python
%loadext autoreload
%autoreload 2
```

````python
from utils import *

TRAIN_DATA_PATH = "SemEval2017-task4-dev.subtask-BD.english.INPUT.txt"
````

````python
data = load_data(TRAIN_DATA_PATH)
data.head()
````


### Train/Validation split

On veut diviser nos données en un jeu d'entraînement et de validation; avec pour objectif de récupérer:
- Les features (X)
- Les cibles/target (y)
- Les labels correspondant à chaque cible

On fera attention à faire en sorte que la distribution de polarité dans le jeu d'entraînement et celle dans celui de 
validation soient égales: on le fait grace au paramètre _stratify_ de la fonction _train_test_split_.

_utils.py_
````python
def prepare_data(
    data: pd.DataFrame, 
    id_column: str,  # tweet ID
    topic_column: str,
    polarity_column: str,
    text_column: str, 
    polarity_to_int: dict[str, int], 
    train_size: float, 
    seed: int
):
    id_ = data[id_column]  
    X = data[text_column]
    labels = data[polarity_column]
    y = labels.apply(lambda p: polarity_to_int.get(p))
    
    X_train, X_val, y_train, y_val, labels_train, labels_val, id_train, id_val = train_test_split(
        X, 
        y, 
        labels, 
        id_,
        train_size=train_size, 
        stratify=y,  # Stratify to deal with imbalanced classes
        random_state=seed
    )
    
    return (X_train, X_val, 
            y_train, y_val, 
            labels_train, labels_val, 
            id_train, id_val)
````

Dans notre environnement jupyter, définissons trois paramètres importants:
- La taille du jeu d'entraînement (ici 70% des données disponibles)
- Le mapping entre la polarité et la cible binaire (0 ou 1)
- La _seed_ permettant de fixer l'aléatoire dans notre expérimentation

_notebook.ipynb_
```python
TRAIN_SIZE = 0.7
POLARITY_TO_INT = {
    "positive": 1, 
    "negative": 0
}
SEED = 42
```

Appelons ensuite la fonction utilitaire dans le notebook:

_notebook.ipynb_
```python
(
    X_train, X_val, 
    y_train, y_val, 
    labels_train, labels_val, 
    id_train, id_val
) = prepare_data(
    data=data_subset, 
    id_column="tweet_id",
    topic_column="topic",
    polarity_column="polarity",
    text_column="tweet_text",
    polarity_to_int=POLARITY_TO_INT,
    train_size=TRAIN_SIZE
)
print(f"{len(X_train)}: length of training data")
print(f"{len(X_val)}: length of validation data")
```

Donnons nous également une idée de la proportion des classes dans notre dataset résultant:

_utils.py_
````python
import altair as alt
import numpy as np


def get_target_statistics(labels: np.ndarray, log_scale: bool, title: str) -> alt.Chart:
    values, counts = np.unique(labels, return_counts=True)
    data = pd.DataFrame({"values":values, "counts": counts})
    
    base = alt.Chart(
        data, 
        title=title, 
        width=150
    ).encode(
        x=alt.X("values:O", title="Target value"), 
        y=alt.Y("counts:Q", title="Count", scale=alt.Scale(type="log" if log_scale else "linear")), 
        color=alt.condition(alt.datum.values == "positive", alt.value("green"), alt.value("red"))
    )
    
    bars = base.mark_bar()
    text = base.mark_text(dy=-10).encode(text="counts:Q")
    return bars + text
````

_notebook.ipynb_
````python
get_target_statistics(labels_train, log_scale=False, title="Train target statistics") | \
get_target_statistics(labels_val, log_scale=False, title="Validation target statistics")
````

Le graphe obtenu a cette allure:

{{< vega file="spec_1" div_id="spec_1" >}}

On constate que notre jeu d'entrainement et de validation ont chacun environ 30% d'exemples négatifs, ce qui est correct 
au regard des résultats obtenus dans l'analyse exploratoire.

### Définition du modèle et entraînement

Créons notre pipeline _scikit-learn_; faisons attention à équilibrer les performances entre polarité négative et 
positive en attribuant un poids plus important sur les exemples négatifs:

_notebook.ipynb_
```python
pipeline = make_pipeline(
    TfidfVectorizer(), 
    LogisticRegression(class_weight="balanced")
)
```

````python
pipeline_trained = pipeline.fit(X_train, y_train)
````
