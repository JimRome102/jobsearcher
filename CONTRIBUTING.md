# Contributing Guide

## Git Workflow

We use a **feature branch workflow** with pull requests.

### Branch Structure

```
main (production-ready code)
  ├── develop (integration branch)
  └── feature/* (feature branches)
  └── bugfix/* (bug fix branches)
  └── hotfix/* (urgent fixes)
```

### Making Changes

#### 1. Create a Feature Branch

```bash
# Make sure you're on develop
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/your-feature-name

# Examples:
# feature/add-linkedin-api
# feature/improve-email-template
# bugfix/fix-location-filter
```

#### 2. Make Your Changes

```bash
# Edit files
nano src/some_file.py

# Test your changes
python src/main.py search

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add LinkedIn API integration

- Added LinkedIn API client
- Updated job aggregator
- Added rate limiting

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

#### 3. Push to GitHub

```bash
git push origin feature/your-feature-name
```

#### 4. Create Pull Request

1. Go to https://github.com/JimRome102/jobsearcher
2. Click "Pull requests" → "New pull request"
3. Set base: `develop` (not main!)
4. Set compare: `feature/your-feature-name`
5. Fill out the PR template
6. Click "Create pull request"

#### 5. Review & Merge

1. Review the changes
2. Check tests pass
3. Click "Merge pull request"
4. Delete the feature branch

### Commit Message Format

Use conventional commits:

```
feat: add new feature
fix: fix a bug
docs: documentation changes
style: formatting, missing semicolons, etc
refactor: code restructuring
test: adding tests
chore: maintenance tasks
```

Examples:
```bash
git commit -m "feat: add salary filter for $175k+ jobs"
git commit -m "fix: location filter now excludes Brooklyn"
git commit -m "docs: update README with installation steps"
git commit -m "refactor: simplify AI matching logic"
```

### When to Create a PR

**Always create a PR for:**
- New features
- Bug fixes
- Configuration changes
- Documentation updates

**Direct commits to main: NEVER** (except initial setup)

### Branch Protection Rules

**main branch:**
- ✅ Protected
- ✅ Require pull request reviews
- ✅ No direct pushes

**develop branch:**
- Pull requests recommended
- Can merge from feature branches

### Example Workflow

```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/add-indeed-api

# Make changes
echo "# Indeed API integration" >> src/indeed_api.py
git add .
git commit -m "feat: add Indeed API client"

# Push and create PR
git push origin feature/add-indeed-api
# Then create PR on GitHub

# After PR is merged
git checkout develop
git pull origin develop
git branch -d feature/add-indeed-api
```

## Testing Before PR

Always test locally before creating a PR:

```bash
# Run job search
python src/main.py search

# Check email sent
# Check terminal output for errors
# Verify database updated
```

## Code Review Checklist

When reviewing PRs:
- [ ] Code is clean and readable
- [ ] No secrets committed (.env excluded)
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages are descriptive
- [ ] No breaking changes (or documented)

---

**Questions?** Check README.md or create an issue.
