# P1-C — Operator Mode

Status: IN REVIEW

## Goal
Produire le premier épisode réel sans dépendance à une API de génération externe.

## Architecture opérationnelle

TOPIC
→ RESEARCH par ChatGPT avec recherche web et sources vérifiables
→ SCRIPT par ChatGPT
→ FACT_CHECK par ChatGPT contre les sources retenues
→ STORYBOARD par ChatGPT
→ artefacts versionnés dans GitHub
→ gate locale `validateTextBundle()`
→ CI GitHub

## Autorité
ChatGPT produit les artefacts. GitHub conserve la source de vérité. La CI et les validateurs locaux décident si le bundle respecte les contrats techniques.

Aucune sortie générée n'est canonique avant :
1. présence de sources institutionnelles vérifiables ;
2. traçabilité faits → sources ;
3. traçabilité script/storyboard → faits ;
4. fact-check PASS ;
5. gate locale PASS ;
6. CI PASS.

## Pourquoi ce mode pour le pilote
- aucune clé API supplémentaire ;
- aucune facturation de provider externe ;
- moins de plomberie ;
- contrôle éditorial direct ;
- vitesse maximale pour apprendre sur le premier épisode.

## Évolutivité
Le contrat `TextProvider` de P1-B reste disponible pour une industrialisation ultérieure. Operator Mode ne détruit pas l'architecture provider-neutral ; il évite simplement de l'utiliser avant qu'elle apporte une valeur réelle.

## Preuve P1-C
Premier bundle réel : `episodes/pilot-ciel-bleu/text-bundle.json`.
Research documenté : `episodes/pilot-ciel-bleu/research.md`.

P1-C est créditable quand le bundle pilote passe les tests et le workflow P1 sur la PR.
