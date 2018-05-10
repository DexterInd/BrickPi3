## Installing

You need internet access for the following step(s).

The quickest way for installing the BrickPi3 is to enter the following command:
```
curl -kL dexterindustries.com/update_BrickPi3 | bash
```

Since `dexterindustries.com/update_brickpi3` points to this folder's file called `update_brickpi3.sh` you can also go the classic route and clone the repository, change the directory to this folder and then run the following script:
```
bash update_brickpi3.sh
```

By default, the BrickPi3 package is installed system-wide, [script_tools](https://github.com/DexterInd/script_tools) and [RFR_Tools](https://github.com/DexterInd/RFR_Tools) are updated each time the script is ran.

An example using options appended to the command can be:
```
curl -kL dexterindustries.com/update_brickpi3 | bash -s -- --user-local --no-update-aptget --no-dependencies
```

## Command Options

The options that can be appended to this command are:

* `--no-dependencies` - skip installing any dependencies for the BrickPi3. It's supposed to be used on each consecutive update after the initial install has gone through.
* `--no-update-aptget` - to skip using `sudo apt-get update` before installing dependencies. For this to be useful, `--no-dependencies` has to be not used.
* `--bypass-rfrtools` - skips installing RFR_Tools completely.
* `--bypass-python-rfrtools` - skips installing/updating the python package for  [RFR_Tools](https://github.com/DexterInd/RFR_Tools).
* `--user-local` - install the python package for the BrickPi3 in the home directory of the user. This doesn't require any special read/write permissions: the actual command used is (`python setup.py install --force --user`).
* `--env-local` - install the python package for the BrickPi3 within the given environment without elevated privileges: the actual command used is (`python setup.py install --force`).
* `--system-wide` - install the python package for the BrickPi3 within the sytem-wide environment with `sudo`: the actual command used is (`sudo python setup.py install --force`).

Important to remember is that `--user-local`, `--env-local` and `--system-wide` options are all mutually-exclusive - they cannot be used together.
As a last thing, different versions of it can be pulled by appending a corresponding branch name or tag.

## Installing

For installing the BrickPi3, you should only use the following command:
```
curl -kL dexterindustries.com/update_brickpi3 | bash
```
