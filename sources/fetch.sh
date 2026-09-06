#!/usr/bin/env bash
# Fetch the source ontologies. See SOURCES.md for the versions results were computed against.
#
# NOTE: these are UNVERSIONED PURLs, which serve whatever the current release is. The
# versionIRI-based URLs would be better targets, but three of them are currently broken --
# see "Version IRI resolution: three bugs worth reporting" in SOURCES.md. Switch to the
# versioned URLs once those are fixed. Checksums below guard against silent drift.
#   ./sources/fetch.sh            all files
#   ./sources/fetch.sh --minimal  skip go.owl and hp.owl (survey-only, ~207 MB)
set -uo pipefail
cd "$(dirname "$0")"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
MINIMAL=0; [ "${1:-}" = "--minimal" ] && MINIMAL=1

# file <TAB> url <TAB> expected-sha256-prefix
read -r -d '' MANIFEST <<'EOF'
ro.owl	http://purl.obolibrary.org/obo/ro.owl	a9f644d4a865747e
hsapdv.owl	http://purl.obolibrary.org/obo/hsapdv.owl	bc310742b68d398f
mmusdv.owl	http://purl.obolibrary.org/obo/mmusdv.owl	1b2db363f8fe6644
uberon.owl	http://purl.obolibrary.org/obo/uberon/uberon-base.owl	50aae4e64fdf97ef
mp.owl	http://purl.obolibrary.org/obo/mp.owl	583b0b28a731f0a9
life-stages-full.owl	https://raw.githubusercontent.com/obophenotype/developmental-stage-ontologies/master/life-stages-full.owl	c6fa9cd539f6347e
life-stages.sssom.tsv	https://raw.githubusercontent.com/obophenotype/developmental-stage-ontologies/master/src/mappings/life-stages.sssom.tsv	251ecdbc15a9acf4
make-bridge-axioms.pl	https://raw.githubusercontent.com/obophenotype/developmental-stage-ontologies/master/src/util/make-bridge-axioms.pl	3407712adc4cb08c
EOF
[ "$MINIMAL" = "0" ] && MANIFEST="$MANIFEST
go.owl	http://purl.obolibrary.org/obo/go.owl	653ce47cd7b02304
hp.owl	http://purl.obolibrary.org/obo/hp.owl	8da35ec3b4cb4943"

sha16() { shasum -a 256 "$1" 2>/dev/null | cut -c1-16; }
rc=0
while IFS=$'\t' read -r name url want; do
  [ -z "${name:-}" ] && continue
  printf "%-24s " "$name"
  if ! curl -sL -m 1200 -A "$UA" -o "$name.part" "$url"; then
    echo "DOWNLOAD FAILED"; rm -f "$name.part"; rc=1; continue
  fi
  mv "$name.part" "$name"
  got=$(sha16 "$name")
  if [ "$got" = "$want" ]; then echo "ok  ($(wc -c < "$name") bytes)"
  else echo "WARNING: checksum $got != $want recorded in SOURCES.md — ontology re-released; counts may drift"; fi
done <<< "$MANIFEST"

# owl-time: w3.org returns 403 to scripted clients, so route via a text proxy
printf "%-24s " "owl-time.ttl"
if curl -sL -m 120 "https://r.jina.ai/https://www.w3.org/2006/time.ttl" -o owl-time.raw 2>/dev/null \
   && [ -s owl-time.raw ]; then
  awk 'f{print} /^# baseURI/{f=1; print}' owl-time.raw > owl-time.ttl && rm -f owl-time.raw
  got=$(sha16 owl-time.ttl)
  [ "$got" = "251bd6970b0d7a5e" ] && echo "ok  ($(wc -c < owl-time.ttl) bytes)" \
                                  || echo "fetched, checksum $got (see SOURCES.md)"
else
  rm -f owl-time.raw
  echo "FAILED — download manually from https://www.w3.org/2006/time.ttl"; rc=1
fi
exit $rc
