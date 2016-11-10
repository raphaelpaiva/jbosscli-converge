Jbosscli-converge
=================

Compare desired and current states to generate cli scripts to enforce
resource compliance.

Desired state is read from `desired.json` or from the controller itself,
using the `-c` and `-a` options.

JSON format is the same returned from the REST management interface.

Use `--address` and `--type` to provide the resource address and type in
cli format.


Usage examples
--------------

`python converge.py -c host:management_port -a "user:password" --address "/profile=my_profile/subsystem=datasources" --type data-source --desired desired_state.json`

Will read the data-sources state from the controller at host:port and compare it to the contents of the desired_state.json file. These must be in the same format as `"result"` section returned by the jboss management api. That is:

`{"DS_name": { "attribute": "value", ...}, "Other_DS": {...}}`
