# GitHub CLI API Reference

This document provides a quick reference for the GitHub CLI commands used in this skill.

## `gh pr list`

List and filter pull requests in a repository.

### Basic Usage

```bash
gh pr list
```

### JSON Output Format

The `--json` flag specifies which fields to include in the output. This skill uses the following fields:

```bash
gh pr list \
  --json number,title,state,author,reviews,latestReviews,reviewDecision,reviewRequests,createdAt,updatedAt,headRefName,baseRefName,labels,statusCheckRollup,additions,deletions,changedFiles,files,body,isDraft \
  --limit 100 \
  --search "state:open"
```

### Field Descriptions

#### Basic Fields
- `number`: PR number (integer)
- `title`: PR title (string)
- `state`: PR state ("OPEN", "CLOSED", "MERGED")
- `url`: GitHub URL for the PR
- `id`: GraphQL node ID
- `isDraft`: Boolean indicating if PR is in draft mode

#### Author & Assignees
- `author`: Object with `login` (username), `name`, `avatarUrl`
- `assignees`: Array of user objects
- `mergedBy`: User who merged the PR

#### Review Fields
- `reviewDecision`: Overall review decision
  - `"APPROVED"` - Sufficient approvals
  - `"CHANGES_REQUESTED"` - Changes requested
  - `"REVIEW_REQUIRED"` - Review needed
  - `null` - No specific decision
- `reviews`: Array of all review objects
- `latestReviews`: Array of most recent review per reviewer
- `reviewRequests`: Array of requested reviewers

Each review object contains:
- `author`: User who submitted the review
- `state`: `"APPROVED"`, `"CHANGES_REQUESTED"`, `"COMMENTED"`, `"DISMISSED"`
- `submittedAt`: ISO 8601 timestamp
- `body`: Review comments

#### Timestamps
- `createdAt`: When PR was created (ISO 8601)
- `updatedAt`: When PR was last updated (ISO 8601)
- `closedAt`: When PR was closed (ISO 8601)
- `mergedAt`: When PR was merged (ISO 8601)

#### Branches
- `headRefName`: Source branch name
- `baseRefName`: Target branch name

#### CI/CD Status
- `statusCheckRollup`: Array of check run objects

Each check run object contains:
- `name`: Check/workflow name
- `status`: Current state ("QUEUED", "IN_PROGRESS", "COMPLETED", "PENDING")
- `conclusion`: Final result ("SUCCESS", "FAILURE", "TIMED_OUT", "NEUTRAL", "CANCELLED")
- `startedAt`: ISO 8601 timestamp
- `completedAt`: ISO 8601 timestamp
- `workflow`: Workflow name (for GitHub Actions)

#### Code Changes
- `additions`: Number of lines added (integer)
- `deletions`: Number of lines deleted (integer)
- `changedFiles`: Number of files changed (integer)
- `commits`: Number of commits in PR

#### Other Fields
- `labels`: Array of label objects (each has `name`, `color`)
- `body`: PR description (markdown)
- `comments`: Array of comment objects

### Search Queries

The `--search` flag supports powerful query syntax:

```bash
# By state
gh pr list --search "state:open"

# By author
gh pr list --search "author:@me"
gh pr list --search "author:username"

# By review status
gh pr list --search "review:none"          # No reviews yet
gh pr list --search "review:required"      # Review required
gh pr list --search "review:approved"      # Approved
gh pr list --search "review:changes_requested"  # Changes requested

# By status checks
gh pr list --search "status:success"       # CI passing
gh pr list --search "status:failure"       # CI failing
gh pr list --status:pending               # CI pending

# By time
gh pr list --search "created:<2025-04-01"  # Created before date
gh pr list --search "updated:>2025-04-01"  # Updated after date

# Combine queries
gh pr list --search "state:open review:required status:success"
```

### Filters

```bash
# Filter by author
gh pr list --author "@me"

# Filter by assignee
gh pr list --assignee "@me"

# Filter by branch
gh pr list --head "feature-branch"
gh pr list --base "main"

# Limit results
gh pr list --limit 50

# Specify repository
gh pr list --repo owner/repo
```

### Template Output

You can format output with templates:

```bash
gh pr list --template '{{.number}}: {{.title}} ({{timeSince .createdAt}}){{"\n"}}'
```

## `gh pr checks`

Show CI status for a specific PR.

```bash
gh pr checks <pr-number>
```

### Options

```bash
# Watch checks until completion
gh pr checks <pr-number> --watch

# Show only required checks
gh pr checks <pr-number> --required

# JSON output
gh pr checks <pr-number> --json name,state,conclusion
```

## `gh pr view`

View detailed information about a PR.

```bash
gh pr view <pr-number>
```

### JSON Output

```bash
gh pr view <pr-number> --json author,reviews,reviewRequests,comments
```

## Examples

### Get all open PRs with passing CI

```bash
gh pr list --search "state:open status:success" \
  --json number,title,author,createdAt,reviewDecision \
  --limit 100
```

### Get PRs waiting for review

```bash
gh pr list --search "review:required" \
  --json number,title,author,reviewRequests,latestReviews \
  --limit 100
```

### Get PRs with failed CI

```bash
gh pr list --search "status:failure" \
  --json number,title,author,statusCheckRollup \
  --limit 100
```

### Get PRs created in the last 7 days

```bash
gh pr list --search "created:$(date -v-7d +%Y-%m-%d)..$(date +%Y-%m-%d)" \
  --json number,title,author,createdAt \
  --limit 100
```

## Authentication

Make sure you're authenticated before running commands:

```bash
gh auth login
gh auth status
```

## Rate Limits

GitHub API has rate limits:
- 60 requests/hour for unauthenticated requests
- 5,000 requests/hour for authenticated requests

The `gh` CLI handles authentication automatically if you've run `gh auth login`.

## Error Handling

Common errors:
- `GraphQL: Could not resolve to a Repository with the name` - Repository not found or no access
- `GraphQL: Resource not accessible by integration` - Insufficient permissions
- `Your token has not been granted the required scopes` - Need to re-authenticate with more permissions

## More Information

- Official docs: https://cli.github.com/manual/gh_pr_list
- Search query syntax: https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests
- GraphQL API: https://docs.github.com/en/graphql
