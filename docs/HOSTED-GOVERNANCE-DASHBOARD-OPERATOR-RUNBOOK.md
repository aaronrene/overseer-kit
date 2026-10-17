# Hosted read-only dashboard

Configure `hosted_dashboard.enabled: true`, explicit `org_allowlist` entries
(`owner/repo` or an allowed owner) and configured read sources. Launch only with
explicit network authorization: bound `ok hosted-dashboard --allow-network`.
The default bind is loopback; non-loopback requires the corresponding setting.
The viewer token authenticates viewers and is separate from the optional upstream
read token. Tokens remain process environment/session values, never config files.
Advertised write scopes are refused. Host and repository allowlists constrain
upstream reads; all local mutation routes/verbs are refused.

Repository routes expose roadmap, handover, gates, marker and `next`. Remote
`docs/NEXT.md` is display-only historical data with `actionable: false` until the
local bound service validates its identity and exact revision. Do not execute it
from the hosted display. The viewer cannot publish NEXT or invoke local engines.

FPR-3 tests use fake upstream transport and real loopback sockets. No hosted
service was deployed or authenticated to a real provider during restoration.
