# Pourquoi ? — Roadmap

Status: CANONICAL
Version: 0.4

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
MERGED ✅ — PR #3, commit `e5b42bb75c398c1a744590543e99ea6643815055`.
- interface provider unique ;
- prompts versionnés ;
- orchestrateur stage-by-stage ;
- fact-check bloquant ;
- gate locale finale non contournable ;
- CI verte : run `32499125930`.

### P1-C — Operator Mode
IN REVIEW.
- ChatGPT réalise le research avec recherche web et sources institutionnelles ;
- ChatGPT produit script, fact-check et storyboard ;
- GitHub conserve les artefacts canoniques ;
- les gates locales et la CI restent l'autorité technique ;
- premier bundle réel : `episodes/pilot-ciel-bleu/text-bundle.json` ;
- aucun provider externe ni clé API nécessaire pour le pilote.

## P2 — Voix
Narration française, qualité, découpage, timings et coût.

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
- P1-B : MERGED ✅
- P1-C : IN REVIEW
- P2–P7 : NOT STARTED

## Next exact
Ouvrir la PR P1-C et obtenir une CI verte sur le bundle pilote réel. Si vert, merger P1-C puis démarrer P2 — Voix sur ce même épisode.
