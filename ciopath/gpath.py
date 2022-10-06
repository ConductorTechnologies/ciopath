from __future__ import unicode_literals

"""
A platform independent representation of a path.

It consists of a prefix and a list of components. Prefix may be:
# None (posix)
# C: (or any letter)
# / (UNC)

Components are the parts without separator. ["usr", "julian", "code"]

There are methods to ask for a path to be returned with forwardslashes or
backslashes, with or without the prefix if it exists.

See test_gpath.py for full behavior.
"""

from future.utils import python_2_unicode_compatible
 
import os
import re

# https://regex101.com/r/EeOqb4/1/
RX_PREFIXED_PATH= re.compile(r"^([a-zA-Z]:|\\|\/)[\\\/]+")
RX_PREFIX = re.compile(r"^([a-zA-Z]:|\\|\/)")

# this matches env style variables: e.g. $FOO or ${FOO}
RX_DOLLAR_VAR = re.compile(r"\$\{?([A-Za-z][A-Z,a-z0-9_]+)\}?")


def _expand_context(path, context):
    """
    Replace $ variables in strings.

    Variable names can either be $NAME or ${NAME}

    Return the string
    """
    result = path
    if context:
        for match in RX_DOLLAR_VAR.finditer(path):
            key = match.group(1)
            replacement = context.get(key)
            if replacement is not None:
                result = result.replace("${}".format(key), replacement)
                result = result.replace("${{{}}}".format(key), replacement)
    return result


def _normalize_dots(components, absolute=True):
    currentdir = "."
    parentdir = ".."
    result = []
    if absolute:
        for c in components:
            if c == currentdir:
                pass
            elif c == parentdir:
                if not len(result):
                    raise ValueError("Can't resolve components of absolute path due to '..' overflow.")
                del result[-1]
            else:
                result.append(c)
        return result

    for c in components:
        if c == currentdir:
            pass
        elif c == parentdir:
            if not len(result) or result[-1] == parentdir:
                result.append(parentdir)
            else:    
                del result[-1]
        else:
            result.append(c)
    
    if not result: 
        result="."
    return result



class Path(object):
    def __init__(self, path, **kw):
        """Initialize a generic path.

        If path is a list, then each element will be a component of the path. 
        If it's a string then expand context variables.
        Also expand, env vars and user unless explicitly told not to with the
        no_expand option. 
        """

        self._drive_prefix = None

        if not path:
            raise ValueError("Empty path")

        if isinstance(path, list):
            ipath = path[:]
            match = RX_PREFIX.match(ipath[0])
            self._absolute = False
            if match:
                self._drive_prefix = ipath.pop(0).replace("\\", "/")
                self._absolute = True

            self._components = _normalize_dots(ipath)
        else:
            context = kw.get("context")
            if context:
                path = _expand_context(path, context)

            if not kw.get("no_expand", False):
                path = os.path.expanduser(os.path.expandvars(path))

            match = RX_PREFIXED_PATH.match(path)
 
            if match:
                self._drive_prefix = match.group(1).replace("\\", "/")
                path = RX_PREFIX.sub("", path)
 
            self._absolute = path[0] in ["/", "\\"]

            self._components = _normalize_dots(
                [s for s in re.split("/|\\\\", path) if s],
                self._absolute
            )

        self._depth = len(self._components)

    def _construct_path(self, sep, with_drive_letter=True):
        """Reconstruct path for given path sep."""
        result = sep.join(self._components)
        if len(self._components) and self._components[-1] in [".", ".."]:
            result = "{}{}".format(result, sep)
        if self._absolute:
            result = "{}{}".format(sep, result)
            if with_drive_letter and self._drive_prefix:

                prefix = self._drive_prefix
                if prefix == "/":
                    prefix = sep

                result = "{}{}".format(prefix, result)
        return result

    def fslash(self, **kw):
        """Path with forward slashes. Can include drive letter."""
        with_drive_letter = kw.get("with_drive", True)
        return self._construct_path("/", with_drive_letter)

    def bslash(self, **kw):
        """Path with back slashes. Can include drive letter."""
        with_drive_letter = kw.get("with_drive", True)
        return self._construct_path("\\", with_drive_letter)

    def make_relative_to(self, start):
        """Make this absolute Path relative with respect to the given start folder.

        We don't check that the start folder is in fact a folder. If you give a file instead you may
        get a result with too many '..' components.
        
        We ignore any drive prefixes. This means paths on 2 different Windows drives are considered
        to be on the same drive. This is not a problem for the purpose of this function.

        We don't change the path if it's already relative.
        """
        if not isinstance(start, Path):
            raise TypeError("Start path must be a gpath Path")

        if not (self.absolute and start.absolute):
            """If either are relative, then we don't change the path.
            
            It's impossible to know their relationship.
            """
            return

        components = self._components
        other_components = start._components

        if components == other_components:
             raise ValueError("Paths (without drive prefixes) must be different.")

        # remove the common parts
        while len(components) and len(other_components) and components[0] == other_components[0]:
            components = components[1:]
            other_components = other_components[1:]

        # both or one or none could be empty
        components = [".."] * len(other_components) + components

        if not components:
            components = "."

        self._components = components
        self._drive_prefix = None
        self._absolute = False
        self._depth = len(self._components) # depth is kind of pointless for relative paths. 
        # TODO: Remove depth altogether

    def os_path(self, **kw):
        """Path with slashes for current os. Can include drive letter."""
        with_drive = kw.get("with_drive", True)
        if os.name == "nt":
            return self.bslash(with_drive=with_drive)
        return self.fslash(with_drive=with_drive)

    def __str__(self):
        """Same as fslash, with_drive=True"""
        return self._construct_path("/", True)

    def startswith(self, path):
        return self.fslash().startswith(path.fslash())

    def endswith(self, suffix):
        return self.fslash().endswith(suffix)

    def __len__(self):
        return len(self.fslash())

    def __eq__(self, rhs):
        if not isinstance(rhs, Path):
            raise NotImplementedError
        return self.fslash() == rhs.fslash()

    def __lt__(self, other):
        return (self.fslash() < other.fslash())

    def __hash__(self):
        return hash(self.fslash())

    def __ne__(self, rhs):
        return not (self == rhs)

    @property
    def depth(self):
        return self._depth

    @property
    def drive_letter(self):
        return self._drive_prefix or ""

    @property
    def absolute(self):
        return self._absolute

    @property
    def is_unc(self):
        return self._drive_prefix in ["/", "\\"]

    @property
    def relative(self):
        return not self._absolute

    @property
    def components(self):
        return self._components or []

    @property
    def all_components(self):
        if self._drive_prefix:
            return ["{}".format(self._drive_prefix)] + self.components
        else:
            return self.components

    @property
    def tail(self):
        return self._components[-1] if self._components else None
