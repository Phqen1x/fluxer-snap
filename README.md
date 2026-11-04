# Fluxer snap

Unofficial snap package for [Fluxer](https://fluxer.app), an instant messaging
and VoIP desktop app. It repackages the official `.deb` from
`pkgs.fluxer.com` (an Electron app) as a `core24` snap.

## Install from the Snap Store

```sh
sudo snap install fluxer
```

Or find it in the Snap Store / App Center. Updates arrive automatically.

If your microphone, camera or saved logins don't work, connect the
permissions below.

```sh
sudo snap connect fluxer:audio-record              # microphone
sudo snap connect fluxer:camera                    # webcam
sudo snap connect fluxer:password-manager-service  # saved logins / keyring
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
sudo snap connect fluxer:password-manager-service  # saved logins / keyring
sudo snap connect fluxer:snapd-control             # in-app update button
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
`snap/snapcraft.yaml`, builds the snap, publishes it to the **edge** channel
and commits the change. You can also run it by hand from the Actions tab
(tick "force" to rebuild without a new release).

It needs a repository secret named `SNAPCRAFT_STORE_CREDENTIALS`:

```sh
snapcraft export-login --snaps fluxer --channels edge \
  --acls package_access,package_push,package_update,package_release -
```

Promote edge to `beta`/`candidate`/`stable` yourself once you've tested it.

### The in-app update button

Fluxer's "update available" button just opens `fluxer.app/download` in a
browser, which is no use for a snap. The snap wraps `xdg-open`
(`snap/local/xdg-open`) and, for that URL only, runs `snap/local/fluxer-refresh`
instead. It asks whether to:

- **Refresh**: update on the channel you're already tracking, or
- **Refresh to edge**: switch to `latest/edge` and update.

Switching to edge is sticky. To go back, run
`sudo snap refresh fluxer --channel=latest/stable`.

The refresh talks to snapd, so it needs the `snapd-control` interface:

```sh
sudo snap connect fluxer:snapd-control
```

Without it the button opens the app's page in the Snap Store instead.
`snapd-control` is a privileged interface, so the Snap Store requires manual
approval before it can be auto-connected. Request it on the
[snapcraft forum](https://forum.snapcraft.io/c/store-requests/19).

### Manual update

Check the current version in the apt repo:

```sh
curl -fsSL https://pkgs.fluxer.com/deb/dists/stable/main/binary-amd64/Packages
```

Then set `source` and `source-checksum` (the `Filename` and `SHA256` fields)
in `snap/snapcraft.yaml` and rebuild.

## Known limitations

- amd64 only (upstream also ships arm64, which isn't wired up here).
- `grade: devel`; switch to `stable` before publishing to the Snap Store.
- The permissions requested are best guesses for a chat and voice app. If
  something is blocked, `snappy-debug` shows which interface is missing.
- Unofficial and not affiliated with Fluxer Platform AB.
