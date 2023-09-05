# GnuPG steps

In this folder we store scripts and documentation around the gpg key we use to sign our helm charts.

We create a main gpg keypar with longer duration. From this keypair we create a subkey with a shorter duration.
The subkey is the one used to sign the helm charts in our workflows.

We use rsa 4096 keys only because helm currently leverages golang/x/openpgp which is basically unmaintained and does
not support the newer ECC algorithms.

The `gpg.sh` file in this folder contains all the steps + helm generation verification in one run, in order to test
the workflow end-to-end.

## Main key creation

This step creates the main key pair

```sh
export GNUPGHOME=~/vp-key-playground
export PASSPHRASE=foobar
export MAIN_KEY_DURATION=20y

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
```

## Create a subkey

```sh
export GNUPGHOME=~/vp-key-playground
export SUB_KEY_DURATION=5y

KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
gpg --batch --passphrase "${PASSPHRASE}" \
    --quick-add-key ${KEY} rsa4096 sign ${SUB_KEY_DURATION}
```

## List all secret keys

```sh
export GNUPGHOME=~/vp-key-playground
gpg --list-secret-keys --with-keygrip
```

## Export main key

This public key is the one needed for verification

```sh
export GNUPGHOME=~/vp-key-playground
KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
gpg --output main-public-key.gpg --export ${KEY}
```

## Export main secret key

```sh
export GNUPGHOME=~/vp-key-playground
KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
gpg --output main-secrey-key.gpg --export-secret-key $KEY
```

## Export subkeys

This is the subkey(s) that needs to be imported in GitHub for the signing

```sh
export GNUPGHOME=~/vp-key-playground
KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
gpg --output "${FILENAME}" --export-secret-subkeys ${KEY}
```

## Revoke a key

These are the steps to revoke a subkey:

```sh
export GNUPGHOME=~/vp-key-playground
KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
gpg --edit-key $KEY
# Pick the subkey to revoke
gpg> revkey rsa4096/DF8F5B4489903C2B
```

## Send keys to keyservers

```sh
export GNUPGHOME=~/vp-key-playground
KEY=$(gpg --list-options show-only-fpr-mbox --list-secret-keys | awk '{print $1}')
gpg --send-keys $KEY
```
