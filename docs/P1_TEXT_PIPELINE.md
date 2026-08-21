# P1 — Pipeline texte

Status: IN PROGRESS

## Goal
Rendre exécutable le contrat `TOPIC → RESEARCH → SCRIPT → FACT_CHECK → STORYBOARD` avant toute génération IA.

## Success
P1 est créditable lorsque :
- un bundle d'épisode possède un contrat TypeScript explicite ;
- les faits doivent référencer des sources connues ;
- le script respecte les 5 sections canoniques et 60–90 secondes ;
- le fact-check couvre chaque fait avant storyboard ;
- le storyboard couvre chaque section ;
- une fixture valide passe et des fixtures cassées échouent ;
- le gate CI est vert.

## Preuve
- `pipeline/contracts/text.ts`
- `pipeline/text/validate.ts`
- `pipeline/text/cli.ts`
- `tests/p1-text-pipeline.test.ts`
- `episodes/fixtures/p1-valid.json`
- workflow `P1 Text Pipeline`

## Hors scope P1-A
- appels LLM réels ;
- recherche web automatisée ;
- choix définitif des providers ;
- génération voix/image/vidéo ;
- publication.

## Next exact
Obtenir un run CI vert sur la PR P1-A. Ensuite brancher la première étape de génération provider-neutral sans affaiblir les gates.
