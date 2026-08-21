# Pourquoi ? — Roadmap

Status: CANONICAL
Version: 0.3

## P0 — Canon projet
Goal: verrouiller les règles produit, contenu, visuel, pipeline et architecture.
Success: les six fichiers canoniques existent et ne se contredisent pas.
Preuve: PR #1 mergée, commit `a23382f1c9dcf59b02f4643513d2515ff487b878`.

## P1 — Pipeline texte
Topic → recherche → sources → script → fact-check → storyboard structuré.

### P1-A — Contrat & gates
MERGED ✅ — PR #2, commit `620ae6a51aa751e6a4f6af928c0177b49d33d7ec`.
- contrats TypeScript ;
- validation de traçabilité sources → faits → script → storyboard ;
- fixture ;
- tests positifs/négatifs ;
- CI verte : run `32498784961`.

### P1-B — Génération provider-neutral
IN PROGRESS.
- interface provider unique ;
- prompts versionnés ;
- orchestrateur stage-by-stage ;
- fact-check bloquant ;
- gate locale finale non contournable ;
- aucun provider réel ni secret dans ce lot.

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
- P1-A : MERGED ✅
- P1-B : IN PROGRESS
- P2–P7 : NOT STARTED

## Next exact
Pousser P1-B, ouvrir la PR draft et obtenir le run CI. Si vert, P1-B devient créditable ; ensuite seulement choisir/brancher le premier adaptateur provider réel.
