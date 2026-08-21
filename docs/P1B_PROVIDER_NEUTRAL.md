# P1-B — Provider-neutral text generation

Status: IN PROGRESS

## Goal
Permettre à n'importe quel provider texte de produire les artefacts P1 sans lui donner le pouvoir de contourner les gates locales.

## Contrat
`TextProvider.generateJson()` reçoit :
- un stage ;
- un identifiant de prompt versionné ;
- l'entrée du stage.

Il retourne une valeur non fiable (`unknown`). L'orchestrateur assemble les sorties puis `validateTextBundle()` reste l'autorité finale.

## Ordre
RESEARCH → SCRIPT → FACT_CHECK → STORYBOARD → LOCAL TEXT GATE

Un fact-check en échec bloque le storyboard.

## Preuve attendue
- provider mock déterministe ;
- orchestration indépendante du provider ;
- prompts v1 versionnés ;
- test prouvant qu'une sortie invalide est refusée ;
- test prouvant qu'un fact-check FAIL interrompt la chaîne ;
- CI verte.

## Hors scope
Aucune clé API et aucun provider réel dans P1-B. L'adaptateur réel sera ajouté séparément après validation du contrat.
