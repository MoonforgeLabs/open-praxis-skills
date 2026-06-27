# macOS launchd Operations

Use environment variables to avoid hard-coded local paths:

```bash
export WATCHTOWER_LAUNCHD_LABEL="com.alex.github-watchtower"
export WATCHTOWER_PLIST_PATH="$HOME/Library/LaunchAgents/$WATCHTOWER_LAUNCHD_LABEL.plist"
```

## Check status

```bash
launchctl print "gui/$(id -u)/$WATCHTOWER_LAUNCHD_LABEL"
```

## Trigger immediately

```bash
launchctl kickstart -k "gui/$(id -u)/$WATCHTOWER_LAUNCHD_LABEL"
```

## Reload

```bash
launchctl bootout "gui/$(id -u)" "$WATCHTOWER_PLIST_PATH"
launchctl bootstrap "gui/$(id -u)" "$WATCHTOWER_PLIST_PATH"
```

## Validate plist

```bash
plutil -lint "$WATCHTOWER_PLIST_PATH"
```

## Logs

Check the log paths configured inside the plist. Common patterns are:

```bash
tail -f logs/launchd.out.log logs/launchd.err.log
```

If a Mac is asleep at the scheduled time, launchd may not run the missed job immediately after wake. Trigger manually with `kickstart` if needed.
