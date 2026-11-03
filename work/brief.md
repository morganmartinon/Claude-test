# Brief : reel « APRÈS » (résultat final, voiture propre)

Demande de Morgan : uniquement le résultat final, PAS un avant/après.
Style : sobre et propre (docs/style-reference.md, « Tes propres reels »), gros plans sur détails et brillance.

## Sortie
- `output/reel_final.mp4` : 1080x1920, 30 fps, H.264 yuv420p (crf 18), AAC stéréo 44,1 kHz, `-movflags +faststart`.
- Durée cible : 15 à 20 s. Retenu : environ 16,7 s.

## Point technique important (rushes)
- 6 rushes 4K HEVC 10 bits **HDR10 (PQ / BT.2020)**, rotation -90 (autorotate ffmpeg = vertical 2160x3840).
- Conversion SDR BT.709 obligatoire dès la découpe, sinon image délavée :
  `zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`
- Éclairage showroom à dominante violet/bleu : à neutraliser légèrement à l'étalonnage.
- 20261029_205046.mp4 est à 29,67 fps : forcer `fps=30`.

## Plans (ordre et durées)
| # | Rush | Début (s) | Durée (s) | Contenu |
|---|---|---|---|---|
| 1 | 20261029_204946 | 0.3 | 2.0 | Ouverture : gros plan phare avant + capot brillant (accroche) |
| 2 | 20261029_205006 | 0.5 | 1.5 | Feu arrière à LED, reflets sur la carrosserie |
| 3 | 20261029_205105 | 0.0 | 1.8 | Aile avant, reflets, début de travelling |
| 4 | 20261029_204946 | 2.8 | 2.0 | Roue et aile avant, reflets |
| 5 | 20261029_205105 | 4.0 | 2.0 | Rétroviseur et flanc |
| 6 | 20261029_205128 | 0.0 | 2.0 | Poignée de porte, reflets sur la portière |
| 7 | 20261029_205046 | 0.5 | 1.5 | Intérieur propre : banquette arrière |
| 8 | 20261029_205105 | 6.0 | 2.0 | Flanc 3/4 arrière, vitres |
| 9 | 20261029_204934 | 1.5 | 1.9 | Fin : plan large de la voiture entière |

Total : 16,7 s. Éviter 20261029_205128 après 3 s (foule visible).

## Transitions
- Coupes sèches entre tous les plans.
- Plan 1 : léger zoom avant progressif (100 % à 106 %).
- Fin : fondu au noir de 0,5 s sur les 0,5 dernières secondes.
- Pas de glitch, pas de fuite de lumière.

## Étalonnage
- Léger : contraste +8 %, saturation +10 %, petite neutralisation de la dominante violette (réduire un peu bleu/magenta), pas de dominante ajoutée. Reflets à conserver (ne pas cramer les hautes lumières).

## Texte
- AUCUN texte (changement de consigne de Morgan) : pas de titre, pas de sous-titre, pas de drawtext.

## Audio
- Pas de musique (Morgan l'ajoute lui-même ensuite). Son d'origine supprimé.
- Piste AAC stéréo 44,1 kHz silencieuse (anullsrc), même durée que la vidéo.
