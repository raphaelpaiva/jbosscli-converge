Jbosscli-converge
=================

Compare desired and current states to generate cli scripts to enforce
resource compliance.

Desired state is read from `desired.json` or from the controller itself,
using the `-c` and `-a` options.

JSON format is the same returned from the REST management interface.

Use `--address` and `--type` to provide the resource address and type in
cli format.
