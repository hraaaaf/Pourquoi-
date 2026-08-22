# Publication closeout — pilote « Pourquoi le ciel est bleu ? »

Statut: **PASS**

## Master publication
- Assemblage: P7 intro + P6 épisode + P7 outro
- Résolution: 1920×1080
- Framerate: 24 fps CFR
- Durée: 84.208333 s
- Total frames: 2021
  - Intro: 53
  - Épisode: 1800
  - Outro: 168
- Audio: AAC 48 kHz
- Loudness mesurée: -14.97 LUFS
- True peak: -1.04 dBTP
- Sous-titres: FR soft track + SRT sidecar, 24 cues
- Chapitres: 9
- Decode errors: 0
- Non-monotonic DTS: 0

## Réparation temporelle P6
Le master P6 contenait 1846 frames décodées pour une timeline nominale de 75 s, avec une rafale de frames partageant pratiquement le même timestamp autour de 5.92 s et des doublons en fin de flux. Le master publication a été reconstruit par échantillonnage selon le presentation timestamp à 24 fps; les timestamps dupliqués privilégient la frame décodée la plus tardive. Résultat: 1800 frames exactes pour les 75 s de l’épisode.

## Hashes
- Master MP4 SHA-256: `c425f5f9e61888d08c4f8b21ba5c573b1c592120ff6cc0c29b9480a73f5a9784`
- SRT SHA-256: `45b79a7222a579592731ab144680af9ff152c0574cbaadae678c7723af7caeeb`

## Gates
- P4 visual gate: PASS
- P5 audio gate: PASS
- P6 master gate: PASS
- P7 branding human gate: PASS
- Publication assembly gate: PASS

Aucun déploiement. Aucun merge vers `main` dans ce closeout.
