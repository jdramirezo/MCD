# AMCD Report

Rapport généré le 26 mai 2026 à partir du workflow Docker AMCD.

## Executive Summary - Résumé exécutif

Cette étude compare 15 alternatives, ici des pays décrits dans `alternatives.csv`, selon une famille de critères économiques et une famille de critères de qualité de vie. Le workflow a été exécuté avec `docker_report_countries.inputs`, le dossier de sortie `docker-report-countries`, la famille `economic` pour les étapes de satisfaction et de dominance, et un seuil ELECTRE de `0.7`.

Le filtrage de satisfaction conserve 11 alternatives et élimine France, Czech Republic, Germany et Poland. La dominance économique réduit ensuite l'ensemble à 6 alternatives non dominées: Canada, Norway, Luxembourg, Switzerland, Sweden et Ireland. Les scores pondérés placent très nettement Switzerland en tête lorsque les poids sont équilibrés ou économiques, tandis que Norway devient le premier choix lorsque la famille `life` est prioritaire. ELECTRE, avec le seuil plus exigeant de `0.7`, confirme un noyau robuste autour de Norway, Luxembourg, Switzerland et Sweden, mais ne donne pas exactement le même vainqueur que les moyennes pondérées dans tous les scénarios.

La conclusion opérationnelle est donc nuancée: Switzerland est la meilleure alternative selon les scores pondérés économiques et équilibrés; Luxembourg est très solide en surclassement économique; Norway est la meilleure option lorsque les critères de vie dominent. Ireland et Canada apparaissent plus fragiles dans les graphes ELECTRE, car ils reçoivent beaucoup de surclassements.

## Study Purpose - Objectif de l'étude

L'objectif inféré des fichiers d'entrée est de comparer des pays selon des critères économiques, sociaux et de qualité de vie afin d'identifier les alternatives les plus attractives selon plusieurs préférences de décision. Les scénarios testent trois positions: équilibre entre économie et vie quotidienne, priorité à l'économie, priorité à la qualité de vie.

La méthode AMCD appliquée ici n'essaie pas de trouver une vérité absolue. Elle sert à structurer le choix: d'abord éliminer les alternatives trop faibles selon les minimums économiques configurés, puis retirer les alternatives économiquement dominées, puis comparer les survivants avec des normalisations, des poids de scénarios et une analyse de surclassement ELECTRE.

## Input Data - Données d'entrée

| Élément | Valeur |
|---|---|
| Configuration Docker | [`../docker_report_countries.inputs`](../docker_report_countries.inputs) |
| Fichier des critères | [`../exemples/countries/criteria.json`](../exemples/countries/criteria.json) |
| Fichier des alternatives | [`../exemples/countries/alternatives.csv`](../exemples/countries/alternatives.csv) |
| Fichier des scénarios | [`../exemples/countries/scenarios.json`](../exemples/countries/scenarios.json) |
| Dossier de sortie | `docker-report-countries` |
| Famille utilisée pour satisfaction/dominance | `economic` |
| Seuil ELECTRE | `0.7` |
| Alternatives initiales | 15 |
| Critères configurés | 16 |
| Critères économiques | 7 |
| Critères de vie | 9 |
| Critères utilisés dans les normalisations | 13 critères numériques à poids positif |

Trois critères configurés n'ont pas d'effet direct dans les sorties normalisées et les scores: `Corruption Perception Index` a un poids `0`, `Language` a un poids `0` et un type catégoriel, et `Religion` a un poids `0`.

## Criteria and Scenarios - Critères et scénarios

| Critère | Famille | Sens | Poids | Minimum | Seuil |
|---|---:|---:|---:|---:|---:|
| Minimum Wage (€/hour) | economic | max | 1 | 15 | 1 |
| Debt (% of GDP) | economic | min | 1 | 30 | 10 |
| Inflation Rate (%) | economic | min | 1 | 3 | 2 |
| GDP per Capita (€) | economic | max | 1 | 40000 | 5000 |
| Government Deficit/Surplus (% of GDP) | economic | min | 1 | 2 | 0 |
| Electricity Prices (€/MWh) | economic | min | 1 | 200 | 20 |
| Tax Burden (% of GDP) | economic | min | 1 | 30 | 5 |
| Homicide Rate (per 100,000 inhabitants) | life | min | 1 | aucun | 0 |
| Education Level (% with upper secondary education) | life | max | 1 | aucun | 0 |
| Citizen Satisfaction | life | max | 1 | aucun | aucun |
| Life Expectancy (years) | life | max | 1 | 80 | aucun |
| Corruption Perception Index | life | min | 0 | aucun | aucun |
| Number of Holidays | life | max | 1 | aucun | aucun |
| Language | life | max | 0 | aucun | aucun |
| Dominant Hair Color | life | max | 1 | aucun | aucun |
| Religion | life | max | 0 | aucun | aucun |

| Scénario | Description | Poids economic | Poids life |
|---|---|---:|---:|
| `equal_weights` | Toutes les familles ont le même poids | 0.5 | 0.5 |
| `economic_higher_weight` | La famille économique est prioritaire | 0.7 | 0.3 |
| `life_higher_weight` | La famille qualité de vie est prioritaire | 0.3 | 0.7 |

## Methodology - Méthodologie

Le workflow Docker exécute les étapes suivantes dans cet ordre:

1. Satisfaction: compare les alternatives aux minimums configurés pour la famille `economic`.
2. Dominance: cherche les alternatives non dominées, toujours sur la famille `economic`.
3. Normalisation: transforme les critères de mesures différentes en valeurs comparables.
4. Scores pondérés: applique les poids de scénario aux critères normalisés.
5. ELECTRE: construit des matrices de concordance, puis des graphes de surclassement en gardant les arcs dont la concordance est strictement supérieure à `0.7`.

Dans cette implémentation, la satisfaction élimine les alternatives qui ne satisfont aucun des minimums économiques sélectionnés. Elle ne supprime donc pas automatiquement une alternative dès qu'elle échoue à un seul minimum. Cette nuance est importante, car plusieurs alternatives conservées échouent à certains minimums tout en satisfaisant au moins un critère économique.

La dominance utilise aussi les seuils des critères: une différence inférieure ou égale au seuil peut être traitée comme une égalité. Les normalisations gardent ensuite seulement les 6 alternatives non dominées et les 13 critères numériques à poids positif.

## Satisfaction Analysis - Analyse de satisfaction

Le fichier [`satisfaction.csv`](satisfaction.csv) indique 11 alternatives retenues et 4 éliminées.

| Alternative retenue | Minimums économiques satisfaits | Lecture |
|---|---:|---|
| Luxembourg | 6 / 7 | Profil économique le plus conforme aux minimums, avec seulement le fardeau fiscal au-dessus du minimum configuré. |
| Switzerland | 6 / 7 | Très conforme; seule la dette dépasse le minimum configuré. |
| Sweden | 4 / 7 | Passe notamment salaire minimum, PIB par habitant, solde public et électricité. |
| Canada | 3 / 7 | Passe salaire minimum, PIB par habitant et électricité, mais échoue sur dette, inflation, déficit et fiscalité. |
| Norway | 3 / 7 | Passe salaire minimum, PIB par habitant et électricité, mais échoue sur dette, inflation, déficit et fiscalité. |
| Ireland | 3 / 7 | Passe PIB par habitant, déficit et fiscalité, mais échoue sur salaire minimum, dette, inflation et électricité. |
| Belgium | 1 / 7 | Retenue car au moins un minimum économique est satisfait, ici l'inflation. |
| Malta | 1 / 7 | Retenue grâce au critère électricité. |
| Denmark | 1 / 7 | Retenue grâce au PIB par habitant. |
| Portugal | 1 / 7 | Retenue grâce au déficit/surplus public. |
| Finland | 1 / 7 | Retenue grâce au salaire minimum. |

| Alternative éliminée | Minimums économiques satisfaits | Interprétation |
|---|---:|---|
| France | 0 / 7 | Ne satisfait aucun des minimums économiques sélectionnés. |
| Czech Republic | 0 / 7 | Ne satisfait aucun des minimums économiques sélectionnés. |
| Germany | 0 / 7 | Ne satisfait aucun des minimums économiques sélectionnés. |
| Poland | 0 / 7 | Ne satisfait aucun des minimums économiques sélectionnés. |

Cette étape joue un rôle de garde-fou. Les minimums représentent des exigences économiques essentielles dans la configuration: salaire, dette, inflation, PIB par habitant, solde public, prix de l'électricité et fiscalité. Avec le comportement actuel du script, elle retire les alternatives totalement incompatibles avec ces exigences, puis laisse la dominance départager les alternatives partiellement compatibles.

## Dominance Analysis - Analyse de dominance

Le fichier [`dominance.csv`](dominance.csv) contient les 6 alternatives non dominées:

| Alternative non dominée |
|---|
| Canada |
| Norway |
| Luxembourg |
| Switzerland |
| Sweden |
| Ireland |

Le journal [`docker_report.log`](docker_report.log) explique les alternatives retirées à cette étape:

| Alternative dominée | Dominée par | Interprétation économique |
|---|---|---|
| Belgium | Canada | Canada est au moins aussi bon, et meilleur sur plusieurs critères économiques selon les seuils. |
| Malta | Switzerland | Switzerland domine Malta sur salaire, inflation, PIB et solde public, avec des égalités sur certains seuils. |
| Denmark | Luxembourg | Luxembourg améliore les principaux critères économiques tout en restant au moins équivalent sur les autres. |
| Portugal | Luxembourg | Luxembourg domine Portugal sur presque toute la famille économique. |
| Finland | Luxembourg | Luxembourg conserve une supériorité économique malgré des égalités seuilées sur certains critères. |

La dominance construit donc une frontière de Pareto économique. Une alternative non dominée n'est pas forcément la meilleure au total; cela signifie seulement qu'aucune autre alternative retenue ne la bat clairement sur tous les critères économiques considérés.

## Normalisation Outputs - Sorties de normalisation

Les fichiers de normalisation sont dans [`normalised/`](normalised/). Ils prennent comme entrée les 6 alternatives non dominées et 13 critères numériques à poids positif.

| Fichier | Usage | Interprétation |
|---|---|---|
| [`normalised/normalised_max.csv`](normalised/normalised_max.csv) | Scores pondérés | Ramène chaque critère à une échelle relative au maximum observé. Pour un critère à minimiser, une valeur plus faible devient meilleure. |
| [`normalised/normalised_max_min.csv`](normalised/normalised_max_min.csv) | Scores pondérés | Étale chaque critère entre 0 et 100. Cette méthode accentue les écarts entre le meilleur et le moins bon de l'échantillon. |
| [`normalised/normalised_sum.csv`](normalised/normalised_sum.csv) | Scores pondérés | Compare chaque valeur à la somme des valeurs du critère. Les scores sont plus comprimés et les écarts sont moins spectaculaires. |
| [`normalised/normalised_vector.csv`](normalised/normalised_vector.csv) | Scores pondérés | Utilise une norme vectorielle; utile pour comparer des profils globaux sans forcer un écart 0-100. |
| [`normalised/normalised_electre_equal_weights.csv`](normalised/normalised_electre_equal_weights.csv) | ELECTRE | Normalisation dédiée à ELECTRE avec prise en compte des seuils des critères. |
| [`normalised/normalised_electre_economic_higher_weight.csv`](normalised/normalised_electre_economic_higher_weight.csv) | ELECTRE | Même structure de valeurs que les autres fichiers ELECTRE; le scénario change ensuite les poids de concordance. |
| [`normalised/normalised_electre_life_higher_weight.csv`](normalised/normalised_electre_life_higher_weight.csv) | ELECTRE | Même structure de valeurs que les autres fichiers ELECTRE; le scénario change ensuite les poids de concordance. |

Les normalisations expliquent une partie des divergences de classement. `normalised_max_min` amplifie les différences locales entre les 6 alternatives restantes; `normalised_sum` produit des scores plus proches; `normalised_max` et `normalised_vector` donnent des classements plus stables. Une alternative robuste doit donc rester bien placée dans plusieurs normalisations, pas seulement dans une seule.

## Weighted Score Analysis - Analyse des scores pondérés

Le fichier [`weights_results.csv`](weights_results.csv) agrège les critères normalisés selon les trois scénarios. Les poids de famille sont répartis entre les critères de la famille en tenant compte des poids individuels des critères.

### `equal_weights`

| Normalisation | 1er | Score | 2e | Score | 3e | Score |
|---|---|---:|---|---:|---|---:|
| `normalised_max` | Switzerland | 68.84 | Luxembourg | 67.79 | Sweden | 66.13 |
| `normalised_max_min` | Switzerland | 69.62 | Norway | 59.06 | Luxembourg | 57.57 |
| `normalised_sum` | Switzerland | 47.84 | Sweden | 47.71 | Luxembourg | 47.43 |
| `normalised_vector` | Switzerland | 53.70 | Luxembourg | 52.97 | Sweden | 52.43 |

Avec des poids égaux, Switzerland est première dans les quatre méthodes. Luxembourg et Sweden se disputent les places suivantes; Norway devient deuxième uniquement avec `normalised_max_min`. Cela indique que Switzerland a le profil agrégé le plus stable, tandis que le rang entre Luxembourg, Sweden et Norway dépend davantage de la normalisation.

### `economic_higher_weight`

| Normalisation | 1er | Score | 2e | Score | 3e | Score |
|---|---|---:|---|---:|---|---:|
| `normalised_max` | Switzerland | 66.67 | Luxembourg | 64.96 | Sweden | 57.03 |
| `normalised_max_min` | Switzerland | 73.73 | Luxembourg | 63.94 | Norway | 51.35 |
| `normalised_sum` | Switzerland | 56.14 | Luxembourg | 55.64 | Sweden | 54.26 |
| `normalised_vector` | Switzerland | 58.48 | Luxembourg | 57.41 | Sweden | 53.41 |

Quand l'économie pèse `0.7`, Switzerland reste première partout. Luxembourg devient le second choix le plus net, avec des scores proches de Switzerland dans `normalised_max`, `normalised_sum` et `normalised_vector`. Sweden reste généralement troisième, sauf avec `normalised_max_min`, où Norway prend la troisième place.

### `life_higher_weight`

| Normalisation | 1er | Score | 2e | Score | 3e | Score |
|---|---|---:|---|---:|---|---:|
| `normalised_max` | Norway | 76.14 | Sweden | 75.23 | Switzerland | 71.01 |
| `normalised_max_min` | Norway | 66.77 | Switzerland | 65.51 | Sweden | 59.01 |
| `normalised_sum` | Norway | 41.52 | Sweden | 41.15 | Switzerland | 39.55 |
| `normalised_vector` | Norway | 52.41 | Sweden | 51.46 | Switzerland | 48.91 |

Quand la qualité de vie pèse `0.7`, Norway passe première dans les quatre normalisations. Sweden est très compétitive et reste deuxième dans trois méthodes. Switzerland reste forte mais perd sa première place, ce qui montre que son avantage vient surtout du compromis global et de la pondération économique.

Lecture globale des scores pondérés: Switzerland domine les scénarios équilibré et économique; Norway domine le scénario qualité de vie; Luxembourg est le meilleur second choix économique; Sweden est le concurrent le plus stable lorsque la vie quotidienne est fortement pondérée.

## ELECTRE Outranking Analysis - Analyse ELECTRE

Le fichier [`electra/electra_results.txt`](electra/electra_results.txt) contient les matrices de concordance. Dans chaque matrice, la ligne est l'alternative A et la colonne l'alternative B. Une valeur élevée signifie que les critères pondérés soutiennent fortement l'affirmation "A surclasse B". Les images de heatmap montrent toute la matrice; les graphes ne gardent que les arcs dont la concordance est strictement supérieure à `0.7`.

Les valeurs affichées dans les heatmaps sont arrondies. Certains arcs marqués visuellement à `0.70` sont présents dans le graphe parce que la valeur réelle dans le fichier est très légèrement supérieure à `0.7`.

### Scénario `equal_weights`

![Heatmap ELECTRE - poids égaux](electra/heatmap_equal_weights.png)

![Graphe de surclassement ELECTRE - poids égaux](electra/outranking_graph_equal_weights.png)

| Indicateur | Valeur |
|---|---:|
| Alternatives dans le graphe | 6 |
| Arcs de surclassement conservés | 8 |
| Seuil appliqué | > 0.7 |

| Alternative | Arcs sortants | Arcs entrants | Lecture |
|---|---:|---:|---|
| Norway | 2 | 0 | Surclasse fortement Canada et Ireland; n'est surclassée par aucun arc au seuil `0.7`. |
| Luxembourg | 2 | 1 | Surclasse Sweden et Ireland, mais reçoit aussi un arc de Sweden. |
| Switzerland | 2 | 0 | Surclasse Canada et Ireland sans recevoir d'arc au seuil. |
| Sweden | 2 | 1 | Surclasse Luxembourg et Ireland, mais reçoit un arc de Luxembourg. |
| Canada | 0 | 2 | Reçoit des surclassements de Norway et Switzerland. |
| Ireland | 0 | 4 | Alternative la plus surclassée dans ce scénario. |

Les relations les plus fortes sont Norway -> Ireland (`0.86`), Luxembourg -> Ireland (`0.85`), puis plusieurs arcs vers Ireland ou Canada autour de `0.77`. La heatmap montre que Norway, Luxembourg et Switzerland ont des lignes globalement plus foncées que Canada et Ireland. Le graphe confirme que les alternatives robustes ne sont pas seulement celles qui ont un bon score moyen: Norway et Switzerland ne reçoivent aucun arc entrant au seuil `0.7`, tandis que Ireland est systématiquement cible de surclassements.

### Scénario `economic_higher_weight`

![Heatmap ELECTRE - poids économique élevé](electra/heatmap_economic_higher_weight.png)

![Graphe de surclassement ELECTRE - poids économique élevé](electra/outranking_graph_economic_higher_weight.png)

| Indicateur | Valeur |
|---|---:|
| Alternatives dans le graphe | 6 |
| Arcs de surclassement conservés | 12 |
| Seuil appliqué | > 0.7 |

| Alternative | Arcs sortants | Arcs entrants | Lecture |
|---|---:|---:|---|
| Luxembourg | 4 | 0 | Meilleur profil de surclassement économique: surclasse Canada, Norway, Sweden et Ireland. |
| Switzerland | 3 | 0 | Très forte, notamment contre Canada, Norway et Ireland. |
| Norway | 3 | 2 | Surclasse Canada, Sweden et Ireland, mais reçoit des arcs de Luxembourg et Switzerland. |
| Sweden | 1 | 2 | Surclasse Ireland mais est surclassée par Luxembourg et Norway. |
| Ireland | 1 | 4 | Ne surclasse que Canada et reçoit beaucoup d'arcs. |
| Canada | 0 | 4 | Alternative la plus faible dans ce graphe économique. |

Le scénario économique densifie le graphe: 12 arcs contre 8 avec poids égaux. Cela signifie que les poids économiques rendent les préférences pairwise plus tranchées. Luxembourg est ici le signal principal d'ELECTRE: sa ligne est très forte contre Sweden et Ireland (`0.85`), mais aussi au-dessus du seuil contre Canada et Norway. Switzerland reste très solide, avec une concordance de `0.80` contre Canada et `0.75` contre Ireland. Cette lecture nuance les scores pondérés: Switzerland garde le meilleur score moyen, mais ELECTRE donne à Luxembourg le meilleur pouvoir de surclassement économique.

### Scénario `life_higher_weight`

![Heatmap ELECTRE - poids qualité de vie élevé](electra/heatmap_life_higher_weight.png)

![Graphe de surclassement ELECTRE - poids qualité de vie élevé](electra/outranking_graph_life_higher_weight.png)

| Indicateur | Valeur |
|---|---:|
| Alternatives dans le graphe | 6 |
| Arcs de surclassement conservés | 10 |
| Seuil appliqué | > 0.7 |

| Alternative | Arcs sortants | Arcs entrants | Lecture |
|---|---:|---:|---|
| Norway | 3 | 0 | Surclasse Canada, Switzerland et Ireland; c'est le profil ELECTRE le plus fort du scénario. |
| Sweden | 3 | 0 | Surclasse Canada, Luxembourg et Ireland; très robuste quand `life` est prioritaire. |
| Switzerland | 2 | 1 | Surclasse Canada et Ireland, mais reçoit un arc de Norway. |
| Luxembourg | 1 | 1 | Surclasse fortement Ireland, mais est surclassée par Sweden. |
| Canada | 1 | 3 | Ne surclasse que Ireland et reçoit des arcs de Norway, Sweden et Switzerland. |
| Ireland | 0 | 5 | Reçoit un arc de toutes les autres alternatives. |

La heatmap montre un déplacement net vers Norway et Sweden: leurs lignes deviennent plus fortes, et elles n'ont aucun arc entrant au seuil `0.7`. Le graphe est plus sélectif que le scénario économique, mais il confirme très bien le résultat des scores pondérés: Norway devient l'alternative de référence lorsque les critères de vie sont prioritaires, avec Sweden comme concurrente directe. Ireland est la cible de tous les arcs, ce qui indique une faiblesse relative très nette dans les comparaisons ELECTRE de ce scénario.

## Scenario Sensitivity - Sensibilité aux scénarios

| Scénario | Meilleur selon scores pondérés | Meilleur signal ELECTRE | Interprétation |
|---|---|---|---|
| `equal_weights` | Switzerland | Norway, Switzerland et Luxembourg forment le groupe fort | Les scores moyens désignent Switzerland, mais ELECTRE montre un trio/quatuor robuste plutôt qu'un vainqueur unique. |
| `economic_higher_weight` | Switzerland | Luxembourg | Les deux méthodes convergent sur Luxembourg et Switzerland comme meilleurs profils, avec un ordre différent. |
| `life_higher_weight` | Norway | Norway, puis Sweden | Accord fort entre scores pondérés et ELECTRE sur la montée de Norway et Sweden. |

Switzerland est très stable dans les scores pondérés, surtout lorsque l'économie compte autant ou plus que la qualité de vie. Luxembourg est particulièrement robuste en ELECTRE économique, car elle surclasse davantage d'alternatives au seuil `0.7`. Norway est l'alternative la plus sensible positivement au poids de la famille `life`: elle passe de concurrente forte à première claire. Sweden suit le même mouvement, avec un profil de vie qui devient décisif lorsque la pondération change.

Canada et Ireland sont plus fragiles. Canada est souvent dernier ou proche du bas dans les scores pondérés économiques et reçoit beaucoup d'arcs entrants dans ELECTRE. Ireland conserve certains atouts dans les scores, mais les graphes la montrent presque toujours comme l'alternative la plus surclassée.

## Final Interpretation - Interprétation finale

Le résultat ne doit pas être lu comme un classement unique et définitif. Les méthodes racontent trois choses complémentaires.

Premièrement, les scores pondérés donnent un vainqueur clair par préférence: Switzerland pour les scénarios équilibré et économique, Norway pour le scénario qualité de vie. Si la décision doit être expliquée par une moyenne agrégée, ces deux alternatives sont les références principales.

Deuxièmement, ELECTRE introduit une logique plus comparative: une alternative est forte lorsqu'elle surclasse beaucoup d'autres alternatives au-dessus du seuil `0.7` et reçoit peu d'arcs entrants. Avec cette lecture, Luxembourg devient le meilleur profil économique de surclassement, Switzerland reste très forte, et Norway/Sweden dominent lorsque la qualité de vie est prioritaire.

Troisièmement, la robustesse vient de la convergence. Switzerland, Luxembourg, Norway et Sweden restent les alternatives réellement crédibles après toutes les étapes. Canada et Ireland survivent à la dominance économique, mais elles sont moins convaincantes une fois les scores pondérés et ELECTRE pris ensemble.

Conclusion décisionnelle:

| Préférence de décision | Alternative à privilégier | Justification |
|---|---|---|
| Meilleur score pondéré économique ou équilibré | Switzerland | Première dans toutes les normalisations des scénarios `equal_weights` et `economic_higher_weight`. |
| Meilleur surclassement économique ELECTRE | Luxembourg | Plus grand nombre d'arcs sortants dans le graphe économique, sans arc entrant au seuil `0.7`. |
| Priorité à la qualité de vie | Norway | Première dans toutes les normalisations du scénario `life_higher_weight` et meilleur signal ELECTRE du même scénario. |
| Choix robuste de second rang | Sweden | Très forte dès que la famille `life` est importante, avec un graphe ELECTRE favorable dans ce scénario. |

## Limitations and Assumptions - Limites et hypothèses

Les résultats dépendent entièrement des critères, poids, directions, seuils et minimums définis dans les fichiers d'entrée. Aucun fait externe sur les pays n'a été ajouté dans cette interprétation.

La satisfaction et la dominance utilisent uniquement la famille `economic`, conformément à la commande Docker demandée. Les critères de qualité de vie ne participent donc pas au filtrage initial ni à la frontière de dominance; ils interviennent ensuite dans la normalisation, les scores pondérés et ELECTRE.

Le comportement actuel du script de satisfaction élimine les alternatives qui satisfont zéro minimum économique. Si l'intention métier était d'éliminer toute alternative échouant à au moins un minimum, les résultats changeraient fortement.

Le seuil ELECTRE `0.7` est structurant. Un seuil plus bas densifierait les graphes; un seuil plus haut ne garderait que les surclassements les plus forts. Ici, les graphes sont déjà assez sélectifs: 8, 12 et 10 arcs selon les scénarios.

Les normalisations ne sont pas interchangeables. `normalised_max_min` amplifie les écarts; `normalised_sum` les compresse; les conclusions les plus fiables sont celles qui résistent à plusieurs méthodes.

Les critères à poids nul ou non numériques ont un impact limité ou nul dans ce workflow. En particulier, `Corruption Perception Index`, `Language` et `Religion` ne changent pas les scores finaux générés ici.

## Artifact Index - Index des artefacts

| Artefact | Description |
|---|---|
| [`README.md`](README.md) | Résumé automatique des paramètres Docker et des fichiers produits. |
| [`docker_report.log`](docker_report.log) | Journal complet du workflow Docker. |
| [`satisfaction.csv`](satisfaction.csv) | Alternatives retenues et éliminées par l'étape de satisfaction. |
| [`dominance.csv`](dominance.csv) | Alternatives non dominées après dominance économique. |
| [`weights_results.csv`](weights_results.csv) | Scores pondérés par scénario et par méthode de normalisation. |
| [`normalised/normalised_max.csv`](normalised/normalised_max.csv) | Données normalisées par maximum. |
| [`normalised/normalised_max_min.csv`](normalised/normalised_max_min.csv) | Données normalisées min-max. |
| [`normalised/normalised_sum.csv`](normalised/normalised_sum.csv) | Données normalisées par somme. |
| [`normalised/normalised_vector.csv`](normalised/normalised_vector.csv) | Données normalisées vectoriellement. |
| [`normalised/normalised_electre_equal_weights.csv`](normalised/normalised_electre_equal_weights.csv) | Données d'entrée ELECTRE pour `equal_weights`. |
| [`normalised/normalised_electre_economic_higher_weight.csv`](normalised/normalised_electre_economic_higher_weight.csv) | Données d'entrée ELECTRE pour `economic_higher_weight`. |
| [`normalised/normalised_electre_life_higher_weight.csv`](normalised/normalised_electre_life_higher_weight.csv) | Données d'entrée ELECTRE pour `life_higher_weight`. |
| [`electra/electra_results.txt`](electra/electra_results.txt) | Matrices de concordance ELECTRE pour les trois scénarios. |
| [`electra/heatmap_equal_weights.png`](electra/heatmap_equal_weights.png) | Heatmap de concordance pour les poids égaux. |
| [`electra/outranking_graph_equal_weights.png`](electra/outranking_graph_equal_weights.png) | Graphe de surclassement pour les poids égaux. |
| [`electra/heatmap_economic_higher_weight.png`](electra/heatmap_economic_higher_weight.png) | Heatmap de concordance avec priorité économique. |
| [`electra/outranking_graph_economic_higher_weight.png`](electra/outranking_graph_economic_higher_weight.png) | Graphe de surclassement avec priorité économique. |
| [`electra/heatmap_life_higher_weight.png`](electra/heatmap_life_higher_weight.png) | Heatmap de concordance avec priorité qualité de vie. |
| [`electra/outranking_graph_life_higher_weight.png`](electra/outranking_graph_life_higher_weight.png) | Graphe de surclassement avec priorité qualité de vie. |
