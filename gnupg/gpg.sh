#!/bin/bash

set -e -o pipefail

BASEDIR=~/vp-key
KEYRING="${BASEDIR}/keys"
TMPKEYRING="${BASEDIR}/tmpkeys" # This is used as a clean keyring where we import subkey and pubkey to verify the chart only
PASSPHRASE="${PASSPHRASE:-foobar}"

CHART="hello-world"
CHART_TGZ="${CHART}-0.1.0.tgz"

MAIN_KEY_DURATION="20y"
SUB_KEY_DURATION="5y"

trap "rm -f vp" EXIT SIGINT

rm -rf "${KEYRING}"
mkdir -p "${KEYRING}" "${TMPKEYRING}"
chmod 0700 "${KEYRING}" "${TMPKEYRING}"
cd $BASEDIR

function create_key() {
    cat >vp <<EOF
%echo Generating a basic OpenPGP key
Key-Type: RSA
Key-Length: 4096
Name-Real: Validated Patterns
Name-Comment: Team
Name-Email: info@validatedpatterns.io
Expire-Date: ${MAIN_KEY_DURATION}
Passphrase: ${PASSPHRASE}
%commit
%echo done
EOF
    gpg --batch --generate-key vp
}

function create_subkey() {
    echo "Generate subkey"
    KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
    gpg --batch --passphrase "${PASSPHRASE}" \
        --quick-add-key ${KEY} rsa4096 sign ${SUB_KEY_DURATION}
}

function print_keys() {
    gpg --list-secret-keys --with-keygrip
}

function export_main_key() {
    local FILENAME=$1
    rm -f ${FILENAME}
    KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
    echo "Exporting public key ${KEY}"
    gpg --output "${FILENAME}" --export ${KEY}
}

function export_privatekey() {
    local FILENAME=$1
    rm -f ${FILENAME}
    KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
    echo "Exporting subkeys for ${KEY}"
    gpg --output "${FILENAME}" --export-secret-key $KEY
}

function export_subkey() {
    local FILENAME=$1
    rm -f ${FILENAME}
    KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
    echo "Exporting subkeys for ${KEY}"
    gpg --output "${FILENAME}" --export-secret-subkeys ${KEY}
}

export GNUPGHOME="${KEYRING}"
create_key
create_subkey
print_keys
export_main_key vp-public.gpg
export_privatekey vp-secret.gpg
export_subkey vp-subkey-secret.gpg

echo "Testing helm sign"
rm -rf ${CHART}*
helm create "${CHART}"
helm package "${CHART}"

echo "Importing only public key and subkeys into new keyring"
export GNUPGHOME="${TMPKEYRING}"
cat vp-public.gpg | gpg --batch --import
cat vp-subkey-secret.gpg | gpg --batch --import
# We are using pip install git+https://gitlab.com/mbaldessari/helm-sign.git@couple-of-fixes
export GPG_PASSPHRASE=${PASSPHRASE}
helm-sign --gnupg-home "${TMPKEYRING}" "${CHART_TGZ}"

# Since helm only supports old format
gpg --export > "${TMPKEYRING}/pubring.gpg"
helm verify "${CHART_TGZ}"
