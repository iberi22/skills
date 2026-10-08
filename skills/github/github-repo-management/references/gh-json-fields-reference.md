# gh CLI — JSON Field Reference for Repo Operations

> Reference for `--json` field names used with `gh repo view`, `gh repo list`, and related commands.
> Also covers `gh release` and `gh run` JSON fields for CI/release automation.

## gh repo view — Available JSON Fields

```bash
gh repo view owner/repo --json <field1>,<field2>,...
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Repository name |
| `nameWithOwner` | string | "owner/repo" |
| `description` | string | Repo description |
| `url` | string | GitHub URL (e.g. https://github.com/owner/repo) |
| `sshUrl` | string | SSH clone URL |
| `visibility` | string | "PUBLIC" or "PRIVATE" |
| `isPrivate` | bool | true if private |
| `isArchived` | bool | true if archived |
| `isFork` | bool | true if forked |
| `isEmpty` | bool | true if empty repo |
| `isTemplate` | bool | true if template repo |
| `isInOrganization` | bool | true if under org account |
| `defaultBranchRef` | obj `{ name }` | Default branch name |
| `languages` | arr `[{ node: { name }, size }]` | Languages by byte size |
| `primaryLanguage` | obj `{ name }` | Primary language |
| `repositoryTopics` | arr `[string]` | Topics (tags) |
| `createdAt` | ISO datetime | Creation time |
| `updatedAt` | ISO datetime | Last update time |
| `pushedAt` | ISO datetime | Last push time |
| `diskUsage` | int | Disk usage in KB |
| `stargazerCount` | int | Star count |
| `forkCount` | int | Fork count |
| `licenseInfo` | obj `{ name }` | License info |
| `viewerCanAdminister` | bool | Can current user admin? |
| `viewerPermission` | string | "ADMIN", "WRITE", "READ", etc. |
| `viewerSubscription` | string | Watching state |
| `hasIssuesEnabled` | bool | Issues enabled? |
| `hasWikiEnabled` | bool | Wiki enabled? |
| `hasDiscussionsEnabled` | bool | Discussions enabled? |
| `hasProjectsEnabled` | bool | Projects enabled? |
| `homepageUrl` | string | Website URL |
| `mirrorUrl` | string | Mirror URL (if mirrored) |
| `parent` | obj | Parent repo (if forked) |
| `templateRepository` | obj | Template repo (if created from template) |
| `codeOfConduct` | obj | Code of conduct |
| `securityPolicyUrl` | string | Security policy URL |
| `deleteBranchOnMerge` | bool | Auto-delete branches? |
| `mergeCommitAllowed` | bool | Merge commits allowed? |
| `rebaseMergeAllowed` | bool | Rebase merge allowed? |
| `squashMergeAllowed` | bool | Squash merge allowed? |
| `latestRelease` | obj | Latest release info |
| `labels` | arr | Issue labels |
| `milestones` | arr | Milestones |
| `assignableUsers` | arr | Users who can be assigned |
| `mentionableUsers` | arr | Users who can be mentioned |
| `issueTemplates` | arr | Issue templates |
| `pullRequestTemplates` | arr | PR templates |
| `fundingLinks` | arr | Funding links |
| `watchers` | arr | Watchers |
| `contactLinks` | arr | Contact links |
| `openGraphImageUrl` | string | OG image URL |
| `usesCustomOpenGraphImage` | bool | Custom OG image? |

## gh repo list — JSON Fields

Same as above, plus:

```bash
gh repo list owner --json name,description,visibility,updatedAt --limit 50
```

## gh release view — JSON Fields

```bash
gh release view v1.0.0 --json name,tagName,createdAt,body,url
```

| Field | Description |
|-------|-------------|
| `name` | Release title |
| `tagName` | Tag name |
| `body` | Release notes (markdown body) |
| `createdAt` | ISO datetime |
| `url` | Release URL |
| `isDraft` | Draft status |
| `isPrerelease` | Pre-release status |
| `assets` | Release assets/files |

## gh run view — JSON Fields

```bash
gh run view <RUN_ID> --json name,status,conclusion,workflowName,headBranch,createdAt
```

| Field | Description |
|-------|-------------|
| `name` | Run display name |
| `status` | "queued", "in_progress", "completed" |
| `conclusion` | "success", "failure", "cancelled", null |
| `workflowName` | Workflow file name |
| `headBranch` | Branch |
| `createdAt` | ISO datetime |
| `headCommit` | Commit SHA |
| `jobs` | List of jobs in the run |

## Common Patterns

### Get repo info and extract key fields

```bash
# Single value
gh repo view owner/repo --json visibility --jq '.visibility'

# Multiple fields as bash variables
eval "$(gh repo view owner/repo --json name,visibility,defaultBranchRef | jq -r '
  "REPO_NAME=\(.name)\nREPO_VISIBILITY=\(.visibility)\nREPO_BRANCH=\(.defaultBranchRef.name)
')"

# Check if repo is private
if [ "$(gh repo view owner/repo --json isPrivate --jq '.isPrivate')" = "true" ]; then
  echo "Private repo"
fi
```

### List repos by visibility

```bash
# Private repos only
gh repo list owner --visibility private --json name,updatedAt --limit 30

# Public repos only
gh repo list owner --visibility public --json name,description --limit 30
```

### Get primary language and license

```bash
gh repo view owner/repo --json primaryLanguage,licenseInfo --jq '{lang: .primaryLanguage.name, license: .licenseInfo.name}'
```
