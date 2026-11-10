# Synthetic GitHub activity display test

These commits were generated on November 19, 2026, solely to test how GitHub
attributes and displays backdated Git author timestamps. They do not represent
development work performed on the historical dates below.

## Test setup

- Repository: `sereeindahouse/Lab11`, default branch `main`.
- Requested profile: `Ariukabro`, using the existing Git author identity.
- Tool: `fake-git-history` version `1.0.3` from PyPI.
- Requested date range: November 2-19, 2026, inclusive.
- Time zone: `Asia/Ulaanbaatar` (`+0800`); author time is noon on each test date.
- Planned synthetic commits: 3 on November 2-8, 4 on November 9-15, and 3 on
  November 16-19. Existing real commits are retained separately.
- Original history ends at `4f76e68fecf0b0e4f1db0a795e0d2d23256626bd` and is preserved unchanged.

The tool accepts daily counts, so it was invoked once per selected date with
`--commit-per-day 1` and matching start/end dates. Each newly generated commit
was then amended before publication to replace its random temporary text file
with this cumulative test log and a `test: synthetic contribution check` message.
Its generated author date was preserved. Committer timestamps reflect the
actual test run. Application files were not changed.

## Generated entries

| Entry | Synthetic author date | Author time and UTC offset |
| --- | --- | --- |
| 1 | 2026-11-02 | 12:00:00 +08:00 |
| 2 | 2026-11-04 | 12:00:00 +08:00 |
| 3 | 2026-11-06 | 12:00:00 +08:00 |
| 4 | 2026-11-09 | 12:00:00 +08:00 |
| 5 | 2026-11-10 | 12:00:00 +08:00 |

## Interpreting the result

A commit's presence in this repository does not by itself prove that GitHub
includes it on a profile's contribution calendar. Email attribution, branch,
repository eligibility, account participation, and indexing all affect that
result. The profile calendar was empty for this date range before this test.

At the initial check, GitHub reported read permission for `Ariukabro` in this
repository, with no fork or authored issue/pull request found. That participation
requirement may prevent calendar credit even when the commit author links to
the correct profile. GitHub also documents an indexing delay of up to 24 hours.

References: [package](https://pypi.org/project/fake-git-history/1.0.3/),
[contribution criteria](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference),
[indexing and troubleshooting](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions).
