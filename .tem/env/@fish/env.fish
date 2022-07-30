function T --wraps "make -C tests"
    make -C (tem find --root tem)/tests $argv
end
alias m make
set -gx TEM_PROJECTROOT (tem find -r tem)
set -gx TEM_EXECUTABLE  "$TEM_PROJECTROOT/tem.py"
set -gx PYTHONPATH      "$TEM_PROJECTROOT:PYTHONPATH"
