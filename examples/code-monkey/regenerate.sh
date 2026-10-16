#!/bin/sh
# Make every generated file of this example again (see GENERATED.md), from code-monkey.mp3 and the sources.
# About 15 minutes with a GPU (the analysis is most of it). Run from anywhere; needs the repository's .venv.
set -e
cd "$(dirname "$0")/../.."
PY=.venv/bin/python; C=arranger-core/scripts; B=south-american-arranger/scripts; A=examples/code-monkey; E=$A/evaluation
# 1. analysis: stems, beats, pitch, words, drums; then the exact click grid (the tracker invents bars here)
$PY $C/analyze.py $A/code-monkey.mp3 $A/work --lyrics $A/lyrics.txt
$PY $C/barmap.py $A/work --grid --anchor 1.07=1
$PY $C/analyze.py $A/code-monkey.mp3 $A/work --lyrics $A/lyrics.txt --force drums,report
# 2. the written-out builds, the checks, the renders and the text sheets
$PY $C/build.py $A/score.py $A/out --work $A/work --lib $B --png --scaling 4.6 --staff-distance 45
for s in lead drums guitar bass; do
    CM_SHEET=$s $PY $C/build.py $A/score.py $A/out-sheets/$s --work $A/work --lib $B --png --scaling 5.6
done
$PY $C/qa.py $A/out --work $A/work > $A/out/qa.txt
$PY $C/render.py $A/out --work $A/work
$PY $B/sheets.py $A/out
# 3. the sheets in git: the short versions, the written-out score, the render
for s in drums bass guitar; do
    $PY $C/compact.py $A/out-sheets/$s/code_monkey_$s.musicxml $A/roadmap_band.py $A/sheets/code_monkey_$s --multirest
done
$PY $C/compact.py $A/out/code_monkey.musicxml $A/roadmap_written.py $A/sheets/code_monkey_full_score
$PY $C/compact.py $A/out-sheets/lead/code_monkey_lead_sheet.musicxml $A/roadmap_written.py $A/sheets/code_monkey_lead_sheet --multirest
cp $A/out/code_monkey.pdf $A/sheets/code_monkey_written_out.pdf
ffmpeg -loglevel error -y -i $A/out/audio/score_full.wav -c:a aac -b:a 160k -movflags +faststart $A/sheets/code_monkey_full_score.m4a
# 4. the evaluation against the master tracks
$PY $C/groundtruth.py $A/out $A/work $E/master-tracks \
    --map V="Lead Vox" BV="Octave Vox" BASS=Bass:bass DR=Drums:drums --activity > $E/groundtruth.txt
$PY $E/extra_checks.py > $E/extra_checks.txt
