#!/usr/bin/env python3
"""Point snap/snapcraft.yaml at the newest Fluxer .deb in the apt repo.

Writes `changed` and `version` to $GITHUB_OUTPUT. Set FORCE=true to report a
change even when the snap already matches the repo.
"""
import os
import re
import sys
import urllib.request

REPO = "https://pkgs.fluxer.com/deb"
PACKAGES = f"{REPO}/dists/stable/main/binary-amd64/Packages"
YAML = "snap/snapcraft.yaml"


def latest_release():
    with urllib.request.urlopen(PACKAGES, timeout=30) as resp:
        text = resp.read().decode()
    for stanza in text.split("\n\n"):
        fields = dict(
            line.split(": ", 1) for line in stanza.splitlines() if ": " in line and line[0] != " "
        )
        if fields.get("Package") == "fluxer":
            return fields["Version"], fields["Filename"], fields["SHA256"]
    sys.exit("fluxer package not found in the apt repo")


def main():
    version, filename, sha256 = latest_release()
    url = f"https://pkgs.fluxer.com/deb/{filename}"

    with open(YAML) as f:
        text = f.read()
    current = re.search(r"^    source: (\S+\.deb)$", text, re.M)
    if current is None:
        sys.exit(f"no .deb source found in {YAML}")

    changed = current.group(1) != url or os.environ.get("FORCE") == "true"
    if current.group(1) != url:
        text = text.replace(current.group(1), url, 1)
        text, n = re.subn(r"(source-checksum: sha256/)\w+", rf"\g<1>{sha256}", text, count=1)
        if n != 1:
            sys.exit(f"no source-checksum found in {YAML}")
        with open(YAML, "w") as f:
            f.write(text)

    print(f"fluxer {version}: {'update needed' if changed else 'snap is up to date'}")
    with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as out:
        out.write(f"changed={'true' if changed else 'false'}\nversion={version}\n")


main()
