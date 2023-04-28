---
title: "Episode 3: résoudre une tâche d'Aspect Based Sentiment Analysis - Baseline et 1ère modélisation"
date: 2023-03-29T09:44:40+02:00
draft: false
tags: ["data science", "sentiment analysis", "absa"]
resources:
- name: spec_1
  src: spec_1.vg.json
featured_image: "meme accuracy.jpeg"
summary: "Dans cet épisode, nous allons construire une baseline pour nous assurer d'être bien partis, nous 
introduirons également un modèle un peu moins bête nous permettant de nous comparer aux participants du challenge"
---

## 📂 Episodes précédents

_Sur la même thématique_:
- {{< page_link path="/posts/2023-S6" >}}
- {{< page_link path="/posts/2023-S7" >}}

Série _résoudre une tâche d'Aspect Based Sentiment Analysis_:
- {{< page_link path="/posts/2023-S8" >}}
- {{< page_link path="/posts/2023-S9" >}}
- **{{< page_link path="/posts/2023-S10" >}}**

## 📌 Sommaire

- 🔫 Introduction
- 👀 Oh la boulette
- 🔧Choix de modélisation
- 🚀 Let's code
- 📖 En résumé

## 🔫 Introduction

Alors, me revoila assez vite pour vous présenter la modélisation qui suit l'analyse exploratoire effectuée précédemment.

Au risque de déplaire à certains, nous allons commencer sobrement avec des méthodes très classiques.

Pourquoi donc? Pour la bonne raison qu'on ne se débarasse pas d'un moustique avec un hélicoptère d'attaque; on commence 
par tenter de le zigouiller avec ses mains, avant de se laisser tenter par la tapette à mouches, la raquette 
électrique, le napalm ou le bazooka pour les plus haîneux d'entre nous.

Ici c'est pareil, notre pipeline _scikit-learn_ simple et basique sera facile à mettre en place, et on va pouvoir 
vérifier rapidement là où il est mauvais. Cela nous permettra de passer à l'étape suivante, en tentant de palier à ses 
limites.

## 👀 Oh la boulette

Cher lecteur, chère lectrice, j'ai pêché. En pensant explorer les bonnes données, nous (la faute est collective bien 
évidemment) avons en fait vu le dataset de _test_ de l'année précédente (SemEval 2016)... 

![meme accuracy](meme%20accuracy.jpeg)

**Par chance, j'ai pu retrouver le package collector intégral, avec les data de _train_, _dev_, _devtest_ et 
_test_.**

Pour la petite anecdote, les données de _train_, _dev_ et _devtest_ sont les mêmes pour les challenges de 2016 et 2017;
seul les jeu de test sont différents. 

Comme les données de test ne sont _normalement_ pas trop éloignées de celles qui servent à entrainer et valider nos 
modèles, on va partir du principe que notre analyse faite précédemment reste valable. Ouf!

On remarque tout de même deux éléments importants: 
- Les topics ne sont pas du tout les mêmes pour chaque dataset.
- Quand un tweet n'est pas récupéré (parce que supprimé ou indisponible), son texte est mis à "Not Available"


> Les données d'entraînement et validation sont les mêmes que pour la compétition SemEval2016, vous pouvez trouver
> les données facilement accessibles sur 
> [GitHub](https://github.com/balikasg/SemEval2016-Twitter_Sentiment_Evaluation/tree/master/src/subtaskD/data)

## 🔧Choix de modélisation

On a pu voir dans un article précédent les différents paradigmes de modélisation, ici nous allons tenter une approche 
_SeqClass_ (classification de phrase) dont les features seront calculées sur une base de _bag-of-words_.

> C'est quoi un _bag-of-words_? Eh bien Jamy, un _sac de mots_ c'est une représentation vectorielle d'un texte (ici un 
> _tweet_), où chaque élément correspond à un _token_ de ton vocabulaire et la valeur associée à cet élément vaut 0 si 
> le _token_ n'apparaît pas dans le texte, et 1 sinon.

Notre modélisation restera classique (pour l'instant 👀):
- _Bag-of-words_ boosté par du _TF-IDF_ *
- Régression Logistique 

En faisant cela, nous effectuons deux hypothèses fortes:
- La présence de certains mots est l'unique déterminant de la polarité
- Comme on a moins de 1% des tweets concernant plusieurs topics, on ne prendra pas en compte le topic dans les features 
de notre modèle

On fera attention à quelques détails néanmoins, pour gérer l'_imbalance_ du _dataset_ concernant le nombre de tweets à 
polarité négative par rapport aux positifs.

> *C'est quoi le TF-IDF? En bref, un mot est considéré important: (1) quand il apparaît dans peu de documents; (2) quand 
> il apparaît de nombreuses fois dans un même document

## 🚀 Let's code

En bon cuisinier, préparons notre recette pour une modélisation réussie. 
Alors pour **entraîner un modèle et analyser ses résultats**, il nous faut:
1. Charger les données, les nettoyer et les convertir dans un format convenable
2. Instancier un modèle, puis l'entraîner
3. Calculer des métriques pour nous informer sur la qualité des résultats
4. Sauvegarder les prédictions fausses quelque part pour les analyser individuellement

Ici on s'en fiche du 4è point parce qu'on est des voyous, et qu'on le fera plus tard dans un autre article.

### Données requises

- Le dataset train/dev/devtest: un bon samaritain l'a téléchargé [ici](https://github.com/balikasg/SemEval2016-Twitter_Sentiment_Evaluation/tree/master/src/subtaskD/data)
- Le dataset test: un zip est disponible [ici](http://alt.qcri.org/semeval2017/task4/data/uploads/semeval2017-task4-test.zip)

### Préparation des données

Comme nous ne sommes pas des cochons mais que nous développons notre modèle dans un notebook (belle antithèse 
remarquez-vous 🤡), nous mettrons en place des fonctions utilitaires pour rendre notre code plus clean.

#### Chargement

_utils.py_
````python
import pandas as pd


def load_data(path: str) -> pd.DataFrame: 
    data = pd.read_csv(path, sep="\t", header=None)
    if len(data.columns) == 5:
        data = data.drop(columns=[4])
    data = data.rename(columns={0: "tweet_id", 1: "topic", 2: "polarity", 3: "tweet_text"})
    return data
````

Par malchance, le dataset de test (téléchargeable dans la section **RESULTS** [ici](https://alt.qcri.org/semeval2017/task4/index.php?id=data-and-tools)) 
n'est pas correctement chargé en utilisant pandas (allez savoir pourquoi, seulement 1069 lignes sur 1185 sont trouvées).

On code donc un autre utilitaire pour charger ces données:


````python
def load_test(path: str) -> pd.DataFrame:
    with open(path) as file:
        records = [l.strip().split("\t") for l in file.readlines()]
    test = pd.DataFrame.from_records(records, columns=["tweet_id", "topic", "polarity", "tweet_text"])
    return test
````

_notebook.ipynb_
```python
%loadext autoreload
%autoreload 2
```

````python
from utils import *

TRAIN_DATA_PATH = "data/subtaskBD.downloaded.tsv"  # Les fichiers ont été renommés et déplacés dans un folder commun
DEV_DATA_PATH = "data/subtaskBD.dev.downloaded.all.tsv"
DEVTEST_DATA_PATH = "data/100_topics_XXX_tweets.topic-two-point.subtask-BD.devtest.gold.downloaded.txt"
TEST_DATA_PATH = "data/SemEval2017-task4-test.subtask-BD.english.txt"
````

````python
train_data = load_data(TRAIN_DATA_PATH)
dev_data = load_data(DEV_DATA_PATH)
devtest_data = load_data(DEVTEST_DATA_PATH)
test_data = load_test(TEST_DATA_PATH)

assert len(train_data.columns) == len(dev_data.columns) == len(devtest_data.columns) == len(test_data.columns)

train_data.head()
````

{{< figure src="chart_2.png" height="150">}}

#### Data cleaning & explicitation des features et targets

On veut enlever les tweets dont le texte est mis à "Not Available", et convertir notre dataframe pandas en une 
collection de tableaux numpy que l'on pourra traiter par notre (futur) modèle:


_utils.py_
````python
def prepare_data(
    data: pd.DataFrame, 
    polarity_to_int: dict[str, int]
) -> tuple[np.ndarray]:
    """
    Clean data, and extracts arrays that will be used.
    
    :returns: a tuple of arrays (ids, topics, polarity, X, y)
    """
    df = data.loc[data.tweet_text != "Not Available"]
    return tuple([
        *(df[c].values for c in df.columns),
        df["polarity"].apply(lambda p: polarity_to_int[p]).values
    ])
````

Dans notre environnement jupyter, définissons deux paramètres importants:
- Le mapping entre la polarité et la cible binaire (0 ou 1)
- La _seed_ permettant de fixer l'aléatoire dans notre expérimentation

_notebook.ipynb_
```python
POLARITY_TO_INT = {
    "positive": 1, 
    "negative": 0
}
SEED = 42
```

Appelons ensuite la fonction utilitaire dans le notebook:

_notebook.ipynb_
```python
ids_train, topics_train, polarity_train, X_train, y_train = prepare_data(train_data, POLARITY_TO_INT)
ids_val, topics_val, polarity_val, X_val, y_val = prepare_data(dev_data, POLARITY_TO_INT)
ids_devtest, topics_devtest, polarity_devtest, X_devtest, y_devtest = prepare_data(devtest_data, POLARITY_TO_INT)
ids_test, topics_test, polarity_test, X_test, y_test = prepare_data(test_data, POLARITY_TO_INT)
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
(get_target_statistics(polarity_train, False, "train") | \
get_target_statistics(polarity_val, False, "dev") | \
get_target_statistics(polarity_devtest, False, "devtest") | \
get_target_statistics(polarity_test, False, "test")).properties(
  title="Répartition de la polarité en fonction du dataset"
)
````

Le graphe obtenu a cette allure:

{{< vega file="spec_1" div_id="spec_1" >}}

On constate que les jeux de _train_, _dev_ et _devtest_ sont relativement homogènes en termes de répartition 
positif/négatif. En revanche, le jeu de test (que l'on ne devrait pas avoir sous les yeux en théorie 👀) montre une 
tendance totalement opposée, puisqu'il y a laregment plus de tweets négatifs que de positifs. 

Mais bon, faisons comme si nous n'avions rien vus sur ce dernier jeu de données 🫣

### Définition du modèle et entraînement

#### Première étape: baseline
Pour s'assurer qu'on ne fait pas de bêtises, il faut absolument créer un modèle baseline identique à celui explicité 
dans le challenge, et vérifier que ses performances sont identiques:


_notebook.ipynb_
```python
pipeline = make_pipeline(
    DummyClassifier(strategy="constant", constant=POLARITY_TO_INT["positive"])
)
pipeline = pipeline.fit(X_train, y_train)  # It does nothing here
```

#### Seconde étapes: métriques

En nous aidant des définitions écrites dans le [papier](https://alt.qcri.org/semeval2017/task4/data/uploads/semeval2017-task4.pdf) 
de recherche du challenge, nous allons implémenter (ou utiliser) les métriques requises:

- \\( AvgRecall = \frac{1}{2} (Recall^P + Recall^N) \\)
- \\( F_1^{PN} = \frac{1}{2} (F_1^P + F_1^N) \\)
- Accuracy

Qui sont basiquement des macro-averaged recall & F1 score, et accuracy.

_utils.py_
````python
from sklearn.metrics import recall_score, f1_score, accuracy_score


def recall_pn(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    recall_positive = recall_score(y_true, y_pred, zero_division=0)
    recall_negative = recall_score(1 - y_true, 1 - y_pred, zero_division=0)
    return 0.5 * (recall_positive + recall_negative)


def f1_pn(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    f1_positive = f1_score(y_true, y_pred, zero_division=0)
    f1_negative = f1_score(1 - y_true, 1 - y_pred, zero_division=0)
    return 0.5 * (f1_positive + f1_negative)
````

Désormais, nous pouvons évaluer le notre classifier baseline sur le jeu de test:

_notebook.ipynb_
````python
test_preds = pipeline.predict(X_test)

test_accuracy = accuracy_score(y_test, test_preds)
test_macro_averaged_recall = recall_pn(y_test, test_preds)
test_macro_averaged_f1 = f1_pn(y_test, test_preds)

print(f"Accuracy: {test_accuracy:.3f}; Recall: {test_macro_averaged_recall:.3f}; F1: {test_macro_averaged_f1:.3f}")
````

En guise de résultats, nous avons:
```
Recall: 0.500; F1: 0.285; Accuracy: 0.398
```
Ce qui correspond effectivement à la baseline spécifiée dans le tableau ci-dessous (baseline B1, avant dernière ligne):

{{< figure src="chart_1.png" height="400" >}}

> Pour rappel, le tableau est disponible dans le [papier scientifique du challenge](https://alt.qcri.org/semeval2017/task4/data/uploads/semeval2017-task4.pdf)

Magnifico! Passons à la suite en créant un véritable classifier cette fois-ci.

#### Troisième étape: un premier vrai classifier
Créons notre pipeline _scikit-learn_; faisons attention à équilibrer les performances entre polarité négative et 
positive en attribuant un poids plus important sur les exemples négatifs:

_notebook.ipynb_
```python
pipeline = make_pipeline(
    TfidfVectorizer(), 
    LogisticRegression(class_weight="balanced", random_state=SEED)
)
pipeline_trained = pipeline.fit(X_train, y_train)
```

Toujours dans le notebook, effectuons l'évaluation sur chaque dataset:

_utils.py_
````python
def evaluate_estimator(estimator, X, y_true):
    y_pred = estimator.predict(X)
    
    accuracy = accuracy_score(y_true, y_pred)
    avg_recall = recall_pn(y_true, y_pred)
    avg_f1 = f1_pn(y_true, y_pred)

    print(f"Recall: {avg_recall:.3f}; F1: {avg_f1:.3f}; Accuracy: {accuracy:.3f}")
````

_notebook.ipynb_
````python
evaluate_estimator(pipeline, X_train, y_train)
evaluate_estimator(pipeline, X_val, y_val)
evaluate_estimator(pipeline, X_devtest, y_devtest)
evaluate_estimator(pipeline, X_test, y_test)
````
Les résultats sont les suivants:
```
# TRAIN 
Recall: 0.944; F1: 0.898; Accuracy: 0.935
# DEV/VALIDATION
Recall: 0.680; F1: 0.679; Accuracy: 0.746
# DEVTEST
Recall: 0.709; F1: 0.692; Accuracy: 0.797
# TEST
Recall: 0.701; F1: 0.682; Accuracy: 0.683
```

Mise à part l'overfitting violent que l'on déguste (-20% sur chaque métrique), on remarque tout de même que nos performances sont très honorables, 
puisque les résultats sur le jeu de test nous positionnerait en 18è place du classement vu plus haut.


Pas mal pour un premier essai non? Alors attendez la suite, on fera encore mieux!


## 📖 En résumé
- On s'est gourrés de dataset les précédents épisodes, mais c'est pas grave parce qu'on reste sur les mêmes types de données
- On s'est donnés pour objectif de faire tourner un premier modèle bien simple et de l'évaluer, ce qu'on a fait
- On s'est assurés de pas faire n'importe quoi en codant et en évaluant une des baselines du challenge
- On a eu de bons résultats!

Et maintenant, on fait quoi?


Alors je sais pas toi mais je suis tenté par tuner notre modèle pour voir jusqu'où on peut pousser les performances d'un 
algorithme bien simple, puis par la suite partir sur quelque chose de plus exotique 🍉 comme des LLM type BERT ou GPT.


A la prochaine!

---