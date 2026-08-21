# Pourquoi ? — Architecture

Status: CANONICAL
Version: 0.1

## Objectif
Une architecture cloud-first, reproductible et suffisamment simple pour le pilote.

## Socle P0
- GitHub : source de vérité, branches, PR, CI.
- GitHub Codespaces : environnement de développement cloud.
- TypeScript / Node.js : orchestration principale.
- Remotion : composition vidéo programmable.
- FFmpeg : traitement audio/vidéo bas niveau.
- Providers IA : interfaces remplaçables, jamais codées en dur dans la logique métier.

## Structure cible
/
- app/
- pipeline/
- episodes/
- assets/
- docs/
- scripts/
- tests/
- .github/workflows/

## Principes techniques
- Config-driven.
- Provider-neutral quand raisonnable.
- Secrets uniquement via variables d'environnement / GitHub Secrets.
- Aucun secret commité.
- Artefacts lourds hors Git lorsque nécessaire.
- Tests ciblés avant rendu coûteux.
- Coûts IA observables dès le pilote.

## Gouvernance des changements
Cette architecture constitue la baseline P0. Tout changement structurel important doit être explicite, versionné et documenté dans `docs/adr/` lorsqu'il devient nécessaire.

## Déploiement
Aucun déploiement public en P0.
Toute mise en production ou déploiement externe requiert une décision explicite.
