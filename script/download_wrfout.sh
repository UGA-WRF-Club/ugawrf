#!/bin/bash -e

RUN_OPTIONS=('00' '03' '06' '09' '12' '15' '18' '21')
URL_WRF_OUTPUTS='https://storage.googleapis.com/wrf-bucket/wrf-outputs'

function wrfout_url () {
    local DATE="${1}"
    local RUN="${2}"
    echo "${URL_WRF_OUTPUTS}/wrfout_d01_${DATE}_${RUN}:00:00"
} # wrfout_url

function validate_run () {
    local RUN="${1}"
    for i in "${RUN_OPTIONS[@]}"; do
        if [ "$i" -eq "${RUN}" ]; then
            return 0
        fi
    done
    >&2 echo "error: invalid RUN argument provided: ${RUN} (must be one of ${RUN_OPTIONS[*]})"
    exit 1
} # validate_run

function download_wrfout () {
    local DATE="${1}"
    local RUN="${2}"
    local WRFOUT_URL="$(wrfout_url ${DATE} ${RUN})"
    echo "Downloading ${WRFOUT_URL} ..."
    curl -O "${WRFOUT_URL}"
    echo "Done!"
} # download_wrfout

function main () {
    local DATE="${1:-$(date +'%Y-%m-%d')}" # use today's date if missing
    local RUN="${2:-00}"                   # use "00" if missing
    validate_run "${RUN}"
    download_wrfout "${DATE}" "${RUN}"
} # main

main ${@}
