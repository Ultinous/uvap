# Notations of the UVAP Documentation

## Shell commands

Lines with monospaced font starting with a `$` (dollar) sign are to be
executed in a shell terminal. The `$` (dollar) sign itself should not
be copied into the terminal.  
Lines starting with `something$` and `something#` are to be treated as
`$` lines, only the following part should be copied. For example:
`<DOCKER># command-to-run` - this means that the command should be run
inside a Docker container.

_Bash_ is the preferred shell program when executing shell commands of
the UVAP Documentation. You may use another kind of shell of your
choice, but in that case, modifications in the shell commands may need
to be made in some cases.

All shell commands in the UVAP Documentation have to run successfully.
Always check the return value of an issued command (`echo $?`). If a
command fails (returns a non-zero return value), do not proceed.
Instead, examine the error message printed by the issued command, and
make any steps necessary for the command to succeed. Ask for help via
email (sent to `support@ultinous.com`), if for any reason you can not
deal with the problem on your own.

If a command is broken into multiple lines, you will see a `\`
(backslash) at the end of each line. All such lines are to be treated
as a single command, and have to be executed at once, copying all the
lines (including the backslashes at the end of the lines) into the
terminal. For example:
```
$ command-to-run argument1 argument2 \
  argument3 argument4
```
