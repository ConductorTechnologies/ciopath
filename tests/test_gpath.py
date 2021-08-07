""" test gpath

   isort:skip_file
"""

import os
import sys
import unittest

try:
    from unittest import mock
except ImportError:
    import mock


SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ciopath.gpath import Path

sys.modules["glob"] = __import__("mocks.glob", fromlist=["dummy"])


class BadInputTest(unittest.TestCase):
    def test_empty_input(self):
        with self.assertRaises(ValueError):
            self.p = Path("")


class RootPath(unittest.TestCase):
    def test_root_path(self):
        self.p = Path("/")
        self.assertEqual(self.p.fslash(), "/")
        self.assertEqual(self.p.bslash(), "\\")

    def test_drive_letter_root_path(self):
        self.p = Path("C:\\")
        self.assertEqual(self.p.fslash(), "C:/")
        self.assertEqual(self.p.bslash(), "C:\\")


class SpecifyDriveLetterUse(unittest.TestCase):
    def test_remove_from_path(self):
        self.p = Path("C:\\a\\b\\c")
        self.assertEqual(self.p.fslash(with_drive=False), "/a/b/c")
        self.assertEqual(self.p.bslash(with_drive=False), "\\a\\b\\c")

    def test_remove_from_root_path(self):
        self.p = Path("C:\\")
        self.assertEqual(self.p.fslash(with_drive=False), "/")
        self.assertEqual(self.p.bslash(with_drive=False), "\\")


class AbsPosixPathTest(unittest.TestCase):
    def setUp(self):
        self.p = Path("/a/b/c")

    def test_fslash_out(self):
        self.assertEqual(self.p.fslash(), "/a/b/c")

    def test_win_path_out(self):
        self.assertEqual(self.p.bslash(), "\\a\\b\\c")


class AbsWindowsPathTest(unittest.TestCase):
    def setUp(self):
        self.p = Path("C:\\a\\b\\c")

    def test_fslash_out(self):
        self.assertEqual(self.p.fslash(), "C:/a/b/c")

    def test_win_path_out(self):
        self.assertEqual(self.p.bslash(), "C:\\a\\b\\c")

    # consider just testing on both platforms
    def test_os_path_out(self):
        with mock.patch("os.name", "posix"):
            self.assertEqual(self.p.os_path(), "C:/a/b/c")
        with mock.patch("os.name", "nt"):
            self.assertEqual(self.p.os_path(), "C:\\a\\b\\c")


class PathStringTest(unittest.TestCase):
    def test_path_emits_string_posix(self):
        input_file = "/path/to/thefile.jpg"
        p = Path(input_file)
        self.assertEqual(str(p), input_file)

    def test_path_emits_string_with_drive(self):
        input_file = "C:/path/to/thefile.jpg"
        p = Path(input_file)
        self.assertEqual(str(p), input_file)

    def test_path_emits_string_relative(self):
        input_file = "path/to/thefile.jpg"
        p = Path(input_file)
        self.assertEqual(str(p), input_file)


class WindowsMixedPathTest(unittest.TestCase):
    def test_abs_in_fslash_out(self):
        self.p = Path("\\a\\b\\c/d/e")
        self.assertEqual(self.p.fslash(), "/a/b/c/d/e")

    def test_abs_in_bslash_out(self):
        self.p = Path("\\a\\b\\c/d/e")
        self.assertEqual(self.p.bslash(), "\\a\\b\\c\\d\\e")

    def test_letter_abs_in_fslash_out(self):
        self.p = Path("C:\\a\\b\\c/d/e")
        self.assertEqual(self.p.fslash(), "C:/a/b/c/d/e")

    def test_letter_abs_in_bslash_out(self):
        self.p = Path("C:\\a\\b\\c/d/e")
        self.assertEqual(self.p.bslash(), "C:\\a\\b\\c\\d\\e")


class MiscPathTest(unittest.TestCase):
    def test_many_to_single_backslashes_bslash_out(self):
        self.p = Path("C:\\\\a\\b///c")
        self.assertEqual(self.p.bslash(), "C:\\a\\b\\c")


class PathExpansionTest(unittest.TestCase):
    def setUp(self):
        self.env = {
            "HOME": "/users/joebloggs",
            "SHOT": "/metropolis/shot01",
            "DEPT": "texturing",
        }

    def test_posix_tilde_input(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("~/a/b/c")
            self.assertEqual(self.p.fslash(), "/users/joebloggs/a/b/c")

    def test_posix_var_input(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("$SHOT/a/b/c")
            self.assertEqual(self.p.fslash(), "/metropolis/shot01/a/b/c")

    def test_posix_two_var_input(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("$SHOT/a/b/$DEPT/c")
            self.assertEqual(self.p.fslash(), "/metropolis/shot01/a/b/texturing/c")

    def test_windows_var_input(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("$HOME\\a\\b\\c")
            self.assertEqual(self.p.bslash(), "\\users\\joebloggs\\a\\b\\c")
            self.assertEqual(self.p.fslash(), "/users/joebloggs/a/b/c")

    def test_tilde_no_expand(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("~/a/b/c", no_expand=True)
            self.assertEqual(self.p.fslash(), "~/a/b/c")

    def test_posix_var_no_expand(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("$SHOT/a/b/c", no_expand=True)
            self.assertEqual(self.p.fslash(), "$SHOT/a/b/c")

    def no_expand_variable_considered_relative(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("$SHOT/a/b/c", no_expand=True)
            self.assertTrue(self.p.relative)
            self.assertFalse(self.p.absolute)

    def expanded_variable_considered_absolute(self):
        with mock.patch.dict("os.environ", self.env):
            self.p = Path("$SHOT/a/b/c", no_expand=False)
            self.assertFalse(self.p.relative)
            self.assertTrue(self.p.absolute)


class PathContextExpansionTest(unittest.TestCase):
    def setUp(self):

        self.env = {
            "HOME": "/users/joebloggs",
            "SHOT": "/metropolis/shot01",
            "DEPT": "texturing",
        }

        self.context = {
            "HOME": "/users/janedoe",
            "FOO": "fooval",
            "BAR_FLY1_": "bar_fly1_val",
            "ROOT_DIR": "/some/root",
        }

    def test_path_replaces_context(self):
        self.p = Path("$ROOT_DIR/thefile.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/some/root/thefile.jpg")

    def test_path_replaces_multiple_context(self):
        self.p = Path("$ROOT_DIR/$BAR_FLY1_/thefile.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/some/root/bar_fly1_val/thefile.jpg")

    def test_path_context_overrides_env(self):
        self.p = Path("$HOME/thefile.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/users/janedoe/thefile.jpg")

    def test_path_leave_unknown_variable_in_tact(self):
        self.p = Path("$ROOT_DIR/$BAR_FLY1_/$FOO/thefile.$F.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/some/root/bar_fly1_val/fooval/thefile.$F.jpg")

    def test_path_replaces_context_braces(self):
        self.p = Path("${ROOT_DIR}/thefile.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/some/root/thefile.jpg")

    def test_path_replaces_multiple_context_braces(self):
        self.p = Path("${ROOT_DIR}/${BAR_FLY1_}/thefile.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/some/root/bar_fly1_val/thefile.jpg")

    def test_path_context_overrides_env_braces(self):
        self.p = Path("${HOME}/thefile.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/users/janedoe/thefile.jpg")

    def test_path_leave_unknown_variable_in_tact_braces(self):
        self.p = Path("${ROOT_DIR}/${BAR_FLY1_}/${FOO}/thefile.$F.jpg", context=self.context)
        self.assertEqual(self.p.fslash(), "/some/root/bar_fly1_val/fooval/thefile.$F.jpg")


class PathLengthTest(unittest.TestCase):
    def test_len_with_drive_letter(self):
        self.p = Path("C:\\aaa\\bbb/c")
        self.assertEqual(len(self.p), 12)

    def test_len_with_no_drive_letter(self):
        self.p = Path("\\aaa\\bbb/c")
        self.assertEqual(len(self.p), 10)

    def test_depth_with_drive_letter(self):
        self.p = Path("C:\\aaa\\bbb/c")
        self.assertEqual(self.p.depth, 3)

    def test_depth_with_no_drive_letter(self):
        self.p = Path("\\aaa\\bbb/c")
        self.assertEqual(self.p.depth, 3)

    def test_depth_with_literal_rel_path(self):
        self.p = Path("aaa\\bbb/c")
        self.assertEqual(self.p.depth, 3)


class AbsolutePathCollapseDotsTest(unittest.TestCase):
    def test_path_collapses_single_dot(self):
        p = Path("/a/b/./c")
        self.assertEqual(p.fslash(), "/a/b/c")

    def test_path_collapses_double_dot(self):
        p = Path("/a/b/../c")
        self.assertEqual(p.fslash(), "/a/c")

    def test_path_collapses_many_single_dots(self):
        p = Path("/a/b/./c/././d")
        self.assertEqual(p.fslash(), "/a/b/c/d")

    def test_path_collapses_many_consecutive_double_dots(self):
        p = Path("/a/b/c/../../d")
        self.assertEqual(p.fslash(), "/a/d")

    def test_path_collapses_many_non_consecutive_double_dots(self):
        p = Path("/a/b/c/../../d/../e/f/../g")
        self.assertEqual(p.fslash(), "/a/e/g")

    def test_path_collapses_many_non_consecutive_mixed_dots(self):
        p = Path("/a/./b/c/../.././d/../././e/f/../g/./")
        self.assertEqual(p.fslash(), "/a/e/g")
        self.assertEqual(p.depth, 3)

    def test_path_collapses_to_root(self):
        p = Path("/a/b/../../")
        self.assertEqual(p.fslash(), "/")
        self.assertEqual(p.depth, 0)

    def test_raise_when_collapse_too_many_dots(self):
        with self.assertRaises(ValueError):
            Path("/a/b/../../../")


class RelativePathCollapseDotsTest(unittest.TestCase):
    def test_resolve_relative_several_dots(self):
        p = Path("./a/b/../../../c/d")
        self.assertEqual(p.fslash(), "../c/d")
        self.assertEqual(p.all_components, ["..", "c", "d"])
        self.assertEqual(p.depth, 3)

    def test_resolve_leading_relative_dots(self):
        p = Path("../c/d")
        self.assertEqual(p.fslash(), "../c/d")

    def test_resolve_leading_relative_dots(self):
        p = Path("../../../c/d")
        self.assertEqual(p.fslash(), "../../../c/d")

    def test_resolve_only_relative_dots(self):
        p = Path("../../../")
        self.assertEqual(p.fslash(), "../../../")

    def test_collapse_contained_components(self):
        p = Path("../../../a/b/../../../")
        self.assertEqual(p.fslash(), "../../../../")

    def test_remove_trailing_dot(self):
        p = Path("../../.././")
        self.assertEqual(p.fslash(), "../../../")

    def test_cwd(self):
        p = Path(".")
        self.assertEqual(p.fslash(), "./")

    def test_down_up_cwd(self):
        p = Path("a/..")
        self.assertEqual(p.fslash(), "./")

    def test_up_down_sibling(self):
        p = Path("../a")
        self.assertEqual(p.fslash(), "../a")

    def test_up_down_sibling_bslash(self):
        p = Path("../a")
        self.assertEqual(p.bslash(), "..\\a")


class PathComponentsTest(unittest.TestCase):
    def test_path_gets_tail(self):
        p = Path("/a/b/c")
        self.assertEqual(p.tail, "c")

    def test_path_gets_none_when_no_tail(self):
        p = Path("/")
        self.assertEqual(p.tail, None)

    def test_path_ends_with(self):
        p = Path("/a/b/cdef")
        self.assertTrue(p.endswith("ef"))

    def test_path_not_ends_with(self):
        p = Path("/a/b/cdef")
        self.assertFalse(p.endswith("eg"))


class RelativePathTest(unittest.TestCase):
    def test_rel_path_does_not_raise(self):
        p = Path("a/b/c")
        self.assertEqual(p.fslash(), "a/b/c")


class EqualityTests(unittest.TestCase):
    def test_paths_equal(self):
        p1 = Path("a/b/c")
        p2 = Path("a/b/c")
        self.assertTrue(p1 == p2)

    def test_same_object_equal(self):
        p1 = Path("a/b/c")
        self.assertTrue(p1 == p1)

    def test_different_paths_equal_false(self):
        p1 = Path("a/b/c")
        p2 = Path("a/b/d")
        self.assertFalse(p1 == p2)

    def test_paths_not_equal(self):
        p1 = Path("a/b/c")
        p2 = Path("a/b/d")
        self.assertTrue(p1 != p2)


class InitializeWithComponentsTests(unittest.TestCase):
    def test_initialize_with_lettered_components(self):
        p = Path(["C:", "a", "b", "c"])
        self.assertEqual(p.fslash(with_drive=True), "C:/a/b/c")

    def test_initialize_with_backslash_unc_components(self):
        p = Path(["\\", "a", "b", "c"])
        self.assertEqual(p.fslash(with_drive=True), "//a/b/c")

    def test_initialize_with_fwslash_unc_components(self):
        p = Path(["/", "a", "b", "c"])
        self.assertEqual(p.fslash(with_drive=True), "//a/b/c")

    def test_initialize_with_unc_components(self):
        p = Path(["/", "a", "b", "c"])
        self.assertEqual(p.bslash(with_drive=True), "\\\\a\\b\\c")

    def test_initialize_with_relative_components(self):
        p = Path(["a", "b", "c"])
        self.assertEqual(p.bslash(with_drive=True), "a\\b\\c")

    def test_initialize_with_relative_components_is_relative(self):
        p = Path(["a", "b", "c"])
        self.assertTrue(p.relative)
        self.assertFalse(p.absolute)


class GetComponentsTests(unittest.TestCase):
    def test_get_all_components(self):
        p = Path("/a/b/c")
        self.assertEqual(p.all_components, ["a", "b", "c"])

    def test_get_all_components_with_drive(self):
        p = Path("C:/a/b/c")
        self.assertEqual(p.all_components, ["C:", "a", "b", "c"])

    def test_get_all_components_with_unc_fwslash(self):
        p = Path("//a/b/c")
        self.assertEqual(p.all_components, ["/", "a", "b", "c"])

    def test_get_all_components_with_unc_backslash(self):
        p = Path("\\\\a\\b\\c")
        self.assertEqual(p.all_components, ["/", "a", "b", "c"])


class UNCTests(unittest.TestCase):
    def test_unc_root_with_drive(self):
        p = Path("\\\\a\\b\\c")
        self.assertEqual(p.fslash(with_drive=True), "//a/b/c")

    def test_unc_is_absolute(self):
        p = Path("\\\\a\\b\\c")
        self.assertTrue(p.absolute)

    def test_unc_root_without_drive(self):
        p = Path("\\\\a\\b\\c")
        self.assertEqual(p.fslash(with_drive=False), "/a/b/c")

    def test_unc_root_with_forward(self):
        p = Path("//a/b/c")
        self.assertEqual(p.fslash(with_drive=True), "//a/b/c")

    def test_is_unc(self):
        p = Path("\\\\a\\b\\c")
        self.assertTrue(p.is_unc)
        p = Path("//a/b/c")
        self.assertTrue(p.is_unc)

    def test_posix_abs_is_not_unc(self):
        p = Path(["/a/b/c"])
        self.assertFalse(p.is_unc)

    def test_relative_is_not_unc(self):
        p = Path(["a/b/c"])
        self.assertFalse(p.is_unc)

    def test_drive_letter_is_not_unc(self):
        p = Path("C:\\aaa\\bbb\\c")
        self.assertFalse(p.is_unc)


if __name__ == "__main__":
    unittest.main()
