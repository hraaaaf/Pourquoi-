# fact-check.v1

## But
Contrôler le script contre les faits et sources fournis.

## Contraintes
- Retourner `pass` uniquement si tous les faits utilisés sont couverts et cohérents avec la recherche.
- `reviewedFactIds` doit couvrir chaque fait du bundle.
- Ne pas corriger silencieusement une source ou inventer une justification.
- En cas de doute matériel, retourner `fail`.
- Sortie JSON uniquement, sans prose autour.
