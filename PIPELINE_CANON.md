# Pourquoi ? — Pipeline Canon

Status: CANONICAL
Version: 0.1

## Pipeline source de vérité
TOPIC
→ RESEARCH
→ SCRIPT
→ FACT_CHECK
→ STORYBOARD
→ ASSETS
→ VOICE
→ COMPOSITION
→ RENDER
→ QA
→ APPROVAL
→ EXPORT

## Gates
Aucun stage aval ne peut devenir canonique si son stage amont requis n'est pas validé.

### Gate 1 — Topic
Question claire, adaptée aux 6–9 ans et compatible avec un épisode court.

### Gate 2 — Research
Sources enregistrées et faits principaux confirmés.

### Gate 3 — Script
Script conforme à CONTENT_CANON.md.

### Gate 4 — Storyboard
Chaque segment du script dispose d'une intention visuelle explicite.

### Gate 5 — Assets
Continuité, droits et cohérence visuelle vérifiés.

### Gate 6 — Audio
Narration française intelligible, naturelle et synchronisable.

### Gate 7 — Render
Vidéo produite sans erreur technique.

### Gate 8 — QA
Factuel + pédagogique + visuel + audio + technique.

### Gate 9 — Human approval
Aucune publication automatique en P0–P6.

## Artefacts par épisode
episodes/<episode-id>/
- episode.yaml
- research.md
- sources.json
- script.md
- storyboard.json
- assets/
- audio/
- render/
- qa.md

## Règle d'idempotence
À entrée et configuration identiques, le pipeline doit pouvoir être relancé sans écraser silencieusement un artefact validé.

## Traçabilité
Chaque artefact généré doit conserver :
- episode_id ;
- version ;
- provider/model si IA ;
- timestamp ;
- hash ou identifiant source si pertinent.
