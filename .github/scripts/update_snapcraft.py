#!/usr/bin/env python3
"""Point snap/snapcraft.yaml at the newest Fluxer .deb for each architecture.

Writes `changed` and `version` to $GITHUB_OUTPUT. Set FORCE=true to report a
change even when the snap already matches the repo.
"""
import os
import re
import sys
import urllib.request

REPO = "https://pkgs.fluxer.com/deb"
ARCHES = ("amd64", "arm64")
YAML = "snap/snapcraft.yaml"


def latest_release(arch):
    with urllib.request.urlopen(f"{REPO}/dists/stable/main/binary-{arch}/Packages", timeout=30) as resp:
        text = resp.read().decode()
    for stanza in text.split("\n\n"):
        fields = dict(
            line.split(": ", 1) for line in stanza.splitlines() if ": " in line and line[0] != " "
        )
        if fields.get("Package") == "fluxer":
            return fields["Version"], f"{REPO}/{fields['Filename']}", fields["SHA256"]
    sys.exit(f"fluxer package not found in the {arch} apt repo")


def main():
    with open(YAML) as f:
        text = f.read()

    changed = os.environ.get("FORCE") == "true"
    versions = set()
    for arch in ARCHES:
        version, url, sha256 = latest_release(arch)
        versions.add(version)
        text, n_url = re.subn(rf"(- on {arch}: )https://\S+\.deb", rf"\g<1>{url}", text)
        text, n_sum = re.subn(rf"(- on {arch}: sha256/)\w+", rf"\g<1>{sha256}", text)
        if (n_url, n_sum) != (1, 1):
            sys.exit(f"could not find the {arch} source and checksum in {YAML}")

    with open(YAML) as f:
        changed = changed or text != f.read()
    with open(YAML, "w") as f:
        f.write(text)

    if len(versions) != 1:
        sys.exit(f"amd64 and arm64 are on different versions: {sorted(versions)}")
    version = versions.pop()

    print(f"fluxer {version}: {'update needed' if changed else 'snap is up to date'}")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as out:
        out.write(f"changed={'true' if changed else 'false'}\nversion={version}\n")


main()
