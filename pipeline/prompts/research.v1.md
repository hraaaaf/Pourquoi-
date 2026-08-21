# research.v1

## But
À partir d'un sujet validé, produire uniquement l'objet `ResearchContract`.

## Contraintes
- Minimum 2 sources HTTPS identifiables.
- Chaque fait possède un `id`, une formulation concise et au moins un `sourceId`.
- Ne jamais inventer une source, un URL ou une citation.
- Si la recherche n'est pas suffisante, échouer explicitement au lieu de compléter par supposition.
- Sortie JSON uniquement, sans prose autour.
