# Pourquoi ? — Roadmap

Status: CANONICAL
Version: 0.2

## P0 — Canon projet
Goal: verrouiller les règles produit, contenu, visuel, pipeline et architecture.
Success: les six fichiers canoniques existent et ne se contredisent pas.
Preuve: PR #1 mergée, commit `a23382f1c9dcf59b02f4643513d2515ff487b878`.

## P1 — Pipeline texte
Topic → recherche → sources → script → fact-check → storyboard structuré.

### P1-A — Contrat & gates
- contrats TypeScript ;
- validation de traçabilité sources → faits → script → storyboard ;
- fixture ;
- tests ;
- CI.

### P1-B — Génération provider-neutral
- interfaces de génération ;
- prompts versionnés ;
- sorties structurées ;
- aucune sortie ne contourne les gates P1-A.

## P2 — Voix
Narration TTS française, qualité, découpage, timings et coût.

## P3 — Images
Génération/gestion des scènes, continuité et identité visuelle.

## P4 — Vidéo
Remotion + FFmpeg, composition, transitions, sous-titres et export.

## P5 — Interface de pilotage
Créer/revoir/corriger/relancer/valider un épisode sans manipulations inutiles.

## P6 — Pilote
Produire et auditer « Pourquoi le ciel est bleu ? » de bout en bout.

## P7 — Industrialisation
Batch, observabilité, coûts, QA automatisée, catalogue d'épisodes et préparation publication.

## Règles de progression
- Un lot n'est crédité que par une preuve vérifiable.
- Aucun lot n'est déclaré terminé sur intention ou prototype partiel.
- Les décisions qui modifient un canon doivent être explicites et versionnées.

## État actuel
- P0 : MERGED ✅
- P1-A : IN PROGRESS
- P1-B–P7 : NOT STARTED

## Next exact
Obtenir un run CI vert sur P1-A, corriger toute défaillance, puis seulement ouvrir P1-B.
