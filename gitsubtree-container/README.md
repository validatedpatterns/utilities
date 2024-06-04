# GIT Subtree container

Git subtree is in git under contrib/ and its support is spotty at times.
Upgrading git has broken our use of the git subtree split command at times.

This is why we use this container where we choose the exact versions of git and
git-subtree carefully. We currently use it to split common subfolders in separate
git repos.

For example a commit to common/acm will push the full history to acm-chart-repo
in our org.
