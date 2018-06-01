# Information for contributors

## Development environment

* [Code and issues are on Github](http://github.com/DARIAH-DE/TopicsExplorer)

### Start hacking

```bash
git clone -b testing git@github.com:DARIAH-DE/TopicsExplorer
cd TopicsExplorer
pipenv insall --dev
```

### Running the tests

Appending `--dev` also installs the testing framework `pytest`. You can run the tests locally from the command-line:

* `pytest` runs all unit tests (functions starting/ending with `test_` or `_test`, respectively).


## Releasing

The _testing_ branch is the integration branch for current developments. The _master_ branch should always contain the latest stable version. 

Pushing to master is protected, you can only push heads that have an "green" status from the integration build. To do so, do the following (from a clean working copy):

1. Prepare everything in `testing`. Don't forget to tune the version number.
2. Merge testing into master. Use `--no-ff` to make sure we get a merge commit: `git checkout master; git merge --no-ff testing`
3. if there are conflicts, resolve them and commit (to master)
4. now, fast-forward-merge master into testing: `git checkout testing; git merge master`. testing and master should now point to the same commit.
5. push testing. This will trigger the integration build, which will hopefully work out fine.
6. when the build has successfully finished, push master.

If something goes wrong, `git reset --hard master origin/master` and try again.
