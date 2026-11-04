# Fluxer snap

Unofficial snap package for [Fluxer](https://fluxer.app), an instant messaging
and VoIP desktop app. It repackages the official `.deb` from
`pkgs.fluxer.com` (an Electron app) as a `core24` snap for amd64 and arm64.

## Install from the Snap Store

```sh
sudo snap install fluxer
```

Or find it in the Snap Store / App Center. Updates arrive automatically.

If your microphone or camera doesn't work, connect the
permissions below.

```sh
sudo snap connect fluxer:audio-record              # microphone
sudo snap connect fluxer:camera                    # webcam
```

## Build

```sh
snapcraft pack
```

Needs [snapcraft](https://snapcraft.io/snapcraft) and LXD or Multipass. Run
`snapcraft clean` first if a previous build failed, since stale part state can
break the next one.

## Install a local build

```sh
sudo snap install --dangerous fluxer_*_amd64.snap
```

Snaps installed with `--dangerous` don't auto-connect any optional
permissions, so connect them yourself:

```sh
sudo snap connect fluxer:audio-record              # microphone
sudo snap connect fluxer:camera                    # webcam
```

Then run `fluxer`, or launch it from your app menu.

## How it works

- **Source:** the `.deb` is downloaded from the Fluxer apt repo at a pinned
  URL and verified with a SHA256 checksum. The snap version is read from
  `/opt/Fluxer/version` inside the deb.
- **Libraries:** the deb's `Depends:` list is mirrored in `stage-packages`,
  since apt dependencies don't carry over into a snap.
- **Extension:** the `gnome` extension provides GTK and the GPU stack.
- **Sandbox:** Fluxer is launched with `--no-sandbox` and the setuid
  `chrome-sandbox` helper is removed, because it can't work inside a snap.
  Confinement comes from snap's own sandbox instead.
- **Desktop entry:** the upstream `app.fluxer.FluxerDesktop.desktop` is used,
  with its icon path patched to resolve inside the snap.

## Updates

### Automatic publishing

`.github/workflows/update-fluxer.yml` checks the Fluxer apt repo every six
hours. When a new `.deb` is out it updates `source` and `source-checksum` in
`snap/snapcraft.yaml`, builds the snap for amd64 and arm64 (the latter on GitHub's arm64 runner), publishes both to the **edge** channel
and commits the change. You can also run it by hand from the Actions tab
(tick "force" to rebuild without a new release).

It needs a repository secret named `SNAPCRAFT_STORE_CREDENTIALS`:

```sh
snapcraft export-login --snaps fluxer --channels edge \
  --acls package_access,package_push,package_update,package_release -
```

Promote edge to `beta`/`candidate`/`stable` yourself once you've tested it.

### Manual update

Check the current version in the apt repo:

```sh
curl -fsSL https://pkgs.fluxer.com/deb/dists/stable/main/binary-amd64/Packages
```

Then set the per-architecture `source` and `source-checksum` entries (the
`Filename` and `SHA256` fields, from `binary-amd64` and `binary-arm64`) in
`snap/snapcraft.yaml` and rebuild.

## Known limitations

- The arm64 build is only built by the GitHub workflow (on an arm64 runner); I haven't run it on real arm64 hardware.
- `grade: devel`; switch to `stable` before publishing to the Snap Store.
- The permissions requested are best guesses for a chat and voice app. If
  something is blocked, `snappy-debug` shows which interface is missing.
- Unofficial and not affiliated with Fluxer Platform AB.
