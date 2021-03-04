""" test gpathlist

   isort:skip_file
"""
 
import sys
import os
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


# Make sure the mocked version of glob is in the sys modules
sys.modules["glob"] = __import__("mocks.glob", fromlist=["dummy"])

# Import gpath_list and anything else that may use glob which will NOT import
# the real glob because it's already here.
from ciopath.gpath_list import PathList
from ciopath.gpath import Path
# from cioseq.sequence import Sequence

# Now import glob because we need to populate it.
import glob # isort:skip

class PathListTest(unittest.TestCase):
    def setUp(self):
        self.env = {
            "HOME": "/users/joebloggs",
            "SHOT": "/metropolis/shot01",
            "DEPT": "texturing",
        }

        self.other_files_on_disk = [
         '/other/file.0001.exr',
         '/other/file.0002.exr',
         '/other/file.0003.exr',
         '/other/file.0004.exr',
         '/other/file.0005.exr',
         '/other/file.0006.exr',
         '/other/file.0007.exr',
         '/other/file.0008.exr',
         '/other/file.0009.exr',
         '/other/file.0010.exr',
         '/other/file.0011.exr',
         '/other/file.0012.exr',
         '/other/file.0013.exr',
         '/other/file.0014.exr',
         '/other/file.0015.exr',
         '/other/file.0016.exr',
         '/other/file.0017.exr',
         '/other/file.0018.exr',
         '/other/file.0019.exr',
         '/other/file.0020.exr']

        self.some_files_on_disk = [
         '/some/file.0001.exr',
         '/some/file.0002.exr',
         '/some/file.0003.exr',
         '/some/file.0004.exr',
         '/some/file.0005.exr',
         '/some/file.0006.exr',
         '/some/file.0007.exr',
         '/some/file.0008.exr',
         '/some/file.0009.exr',
         '/some/file.0010.exr',
         '/some/file.0011.exr',
         '/some/file.0012.exr',
         '/some/file.0013.exr',
         '/some/file.0014.exr',
         '/some/file.0015.exr',
         '/some/file.0016.exr',
         '/some/file.0017.exr',
         '/some/file.0018.exr',
         '/some/file.0019.exr',
         '/some/file.0020.exr']



    def test_init_empty(self):
        d = PathList()
        self.assertEqual(list(d), [])

    def test_init_with_args(self):
        d = PathList("/a/file2", "/a/file3")
        self.assertEqual(len(d), 2)

    def test_adds_paths(self):
        d = PathList()
        d.add(Path("/a/file1"), Path("/a/file2"))
        self.assertEqual(len(d), 2)

    def test_adds_strings(self):
        d = PathList()
        d.add("/a/file1", "/a/file2")
        self.assertEqual(len(d), 2)

    def test_adds_mix(self):
        d = PathList()
        d.add("/a/file1", "/a/file2", Path("/a/file3"))
        self.assertEqual(len(d), 3)


    # remove
    def test_removes_string(self):
        d = PathList()
        d.add("/a/file1", "/a/file2", "/a/file3")
        d.remove("/a/file2")
        self.assertEqual(len(d), 2)

    def test_removes_path(self):
        d = PathList()
        d.add("/a/file1", "/a/file2", "/a/file3")
        d.remove(Path("/a/file2"))
        self.assertEqual(len(d), 2)
        self.assertEqual( list(d)[1],  Path("/a/file3"))

    def test_removes_many(self):
        d = PathList()
        d.add("/a/file1", "/a/file2", "/a/file3")
        d.remove("/a/file2", "/a/file3")
        self.assertEqual(len(d), 1)

    def test_removes_paths_when_list_contains_duplicates(self):
        d = PathList()
        d.add("/a/file1", "/a/file2", "/a/file3", "/a/file2")
        d.remove("/a/file1")
        self.assertEqual(len(d), 2)

    def test_removes_duplicate_when_list_contains_duplicates(self):
        d = PathList()
        d.add("/a/file1", "/a/file2", "/a/file3", "/a/file2", "/a/file3")
        d.remove("/a/file2")
        self.assertEqual(len(d), 2)
 
    def test_does_not_deduplicate_internally_on_removal(self):
        # deduplication is lazy - happens on access
        d = PathList()
        d.add("/a/file1", "/a/file2", "/a/file3", "/a/file2", "/a/file3")
        d.remove("/a/file2")
        self.assertEqual(len(d._entries), 3)


    # just want to make sure expansion works here
    # even though it's tested in gpath_test
    def test_expand_tilde(self):
        with mock.patch.dict("os.environ", self.env):
            d = PathList()
            d.add("~/file1", "~/file2")

            self.assertIn("/users/joebloggs/file1", d)

    def test_expand_envvar(self):
        with mock.patch.dict("os.environ", self.env):
            d = PathList()
            d.add("$SHOT/file1", "$HOME/file2")
            self.assertIn("/metropolis/shot01/file1", d)
            self.assertIn("/users/joebloggs/file2", d)

    def test_dedup_same_paths(self):
        d = PathList()
        d.add(Path("/file1"), Path("/file2"), Path("/file2"))
        self.assertEqual(len(d), 2)
        self.assertIn(Path("/file1"), d)
        self.assertIn(Path("/file2"), d)

    def test_dedup_same_strings(self):
        d = PathList()
        d.add("/file1", "/file2", "/file2")
        self.assertEqual(len(d), 2)
        self.assertIn("/file1", d)
        self.assertIn("/file2", d)

    def test_dedup_contained_file(self):
        d = PathList()
        d.add("/dir1/", "/dir1/file1", "/dir2/file1", "/dir3/file2")
        self.assertEqual(len(d), 3)

    def test_dedup_dirtied_on_add(self):
        d = PathList()
        d.add("/file1")
        self.assertFalse(d._clean)

    def test_dedup_cleaned_on_access_iter(self):
        d = PathList()
        d.add("/file1")
        ls = list(d)
        self.assertTrue(d._clean)

    def test_dedup_cleaned_on_access_len(self):
        d = PathList()
        d.add("/file1")
        ls = len(d)
        self.assertTrue(d._clean)

    def test_dedup_cleaned_on_access_next(self):
        d = PathList()
        d.add("/file1", "/file2", "/file3")
        n = next(d)
        self.assertTrue(d._clean)

    def test_next(self):
        d = PathList()
        d.add("/file1", "/file2", "/file3")
        self.assertEqual(next(d), Path("/file1"))
        self.assertEqual(next(d), Path("/file2"))

    def test_next_fails_after_last(self):
        d = PathList()
        d.add("/file1", "/file2", "/file3")
        next(d)
        next(d)
        next(d)
        with self.assertRaises(StopIteration):
            next(d)

    def test_next_reset_after_add(self):
        d = PathList()
        d.add("/file1", "/file2", "/file3")
        next(d)
        next(d)
        d.add("/file4")
        self.assertEqual(next(d), Path("/file1"))

    def test_common_path_when_common_prefix_in_filename(self):
        d = PathList()
        files = [
            "/users/joebloggs/tmp/dissention/perfect",
            "/users/joebloggs/tmp/disagreement/crimson",
            "/users/joebloggs/tmp/diatribe/belew",
        ]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/users/joebloggs/tmp"))

    def test_common_path(self):
        d = PathList()
        files = [
            "/users/joebloggs/tmp/foobar/test",
            "/users/joebloggs/tmp/baz/fripp",
            "/users/joebloggs/tmp/elephant/corner",
        ]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/users/joebloggs/tmp"))

    def test_common_path_when_one_path_is_the_common_path(self):
        d = PathList()
        files = [
            "/users/joebloggs/tmp",
            "/users/joebloggs/tmp/bolly/operation",
            "/users/joebloggs/tmp/stay/go",
        ]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/users/joebloggs/tmp"))

    def test_common_path_when_lowest_path_is_the_common_path(self):
        d = PathList()
        files = [
            "/users/joebloggs/tmp/foo.txt",
            "/users/joebloggs/tmp/modelman.jpg",
            "/users/joebloggs/tmp/ration.cpp",
            "/users/joebloggs/tmp/bill.project",
        ]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/users/joebloggs/tmp"))

    def test_common_path_drive_letter(self):
        d = PathList()
        files = [
            "C:/users/joebloggs/hello/foo.txt",
            "C:/users/joebloggs/tmp/modelman.jpg",
            "C:/users/joebloggs/tmp/ration.cpp",
            "C:/users/joebloggs/tmp/bill.project",
        ]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("C:/users/joebloggs"))

    # This is not right. There is no common path if drive letters
    # are involved. Need to revisit, and hope that in the
    # meantime  no one renders to two different filesystems in the
    # same render job.
    def test_common_different_drive_letter(self):
        d = PathList()
        files = [
            "D:/users/joebloggs/tmp/foo.txt",
            "D:/users/joebloggs/tmp/modelman.jpg",
            "C:/users/joebloggs/tmp/ration.cpp",
            "C:/users/joebloggs/tmp/bill.project",
        ]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/"))

    def test_common_path_when_single_path(self):
        d = PathList()
        files = ["/users/joebloggs/tmp/foo.txt"]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/users/joebloggs/tmp/foo.txt"))

    def test_common_path_when_duplicate_entries_of_single_path(self):
        d = PathList()
        files = ["/users/joebloggs/tmp/foo.txt",
                 "/users/joebloggs/tmp/foo.txt"]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/users/joebloggs/tmp/foo.txt"))

    def test_common_path_is_none_when_no_entries(self):
        d = PathList()
        self.assertIsNone(d.common_path())

    def test_common_path_is_slash_when_root(self):
        d = PathList()
        files = ["/users/joebloggs/tmp/foo.txt", "/dev/joebloggs/tmp/foo.txt"]
        d.add(*files)
        self.assertEqual(d.common_path(), Path("/"))

    def test_glob_when_files_match_with_asterisk(self):
        glob.populate(self.some_files_on_disk)
        d = PathList()
        file = "/some/file.*.exr"
        d.add(file)
        d.glob()
        self.assertEqual(len(d), 20)

    def test_glob_when_files_match_with_question_mark(self):
        glob.populate(self.some_files_on_disk)
        d = PathList()
        file = "/some/file.00?0.exr"
        d.add(file)
        d.glob()
        self.assertEqual(len(d), 2)

    def test_glob_when_files_match_with_range(self):
        glob.populate(self.some_files_on_disk)
        d = PathList()
        file = "/some/file.000[0-9].exr"
        d.add(file)
        d.glob()
        self.assertEqual(len(d), 9)

    def test_glob_dedups_when_many_files_match(self):
        glob.populate(self.some_files_on_disk)
        d = PathList()
        files = ["/some/file.*.exr", "/some/*.exr"]
        d.add(*files)
        d.glob()
        self.assertEqual(len(d), 20)

    def test_glob_when_files_dont_match(self):
        glob.populate(self.other_files_on_disk)
        d = PathList()
        file = "/some/file.*.exr"
        d.add(file)
        d.glob()
        self.assertEqual(len(d), 0)

    def test_unpacking(self):
        d = PathList()
        d.add(Path("/a/file1"), Path("/a/file2"))
        a, b = d
        self.assertEqual(type(a), Path)

    def test_glob_leaves_non_existent_unglobbable_entries_untouched(self):
        glob.populate(self.some_files_on_disk[:3])
        d = PathList()
        d.add("/some/file.*.exr", "/other/file1.exr", "/other/file2.exr")
        d.glob()
        self.assertEqual(len(d), 5)

    def test_ignore_invalid_glob(self):
        bad_glob = "/path/to/Model[b-a]"
        glob.populate(bad_glob)
        d = PathList()
        d.add(bad_glob)
        d.glob()
        self.assertEqual(list(d)[0].fslash(), bad_glob)

    def test_ignore_invalid_nonexistent_glob(self):
        bad_glob = "/path/to/Model[b-a]"
        d = PathList()
        d.add(bad_glob)
        d.glob()
        self.assertEqual(list(d)[0].fslash(), bad_glob)
 
    def test_empty_list_is_falsy(self):
        self.assertFalse(PathList())

    def test_populated_list_is_truthy(self):
        self.assertTrue(PathList("/file"))


class MissingFilesTest(unittest.TestCase):

    @staticmethod
    def side_effect(arg):
        if "missing" in arg: 
            return False
        else:
            return True

    def setUp(self):

        patcher = mock.patch('os.path.exists')
        self.mock_exists = patcher.start()
        self.mock_exists.side_effect = MissingFilesTest.side_effect
        self.addCleanup(patcher.stop)


    def test_remove_no_missing_file(self):
        d = PathList()
        files = ["/tmp/foo.txt", "/tmp/bar.txt"]
        d.add(*files)
        self.assertEqual(len(d), 2)
        d.remove_missing()
        self.assertEqual(len(d), 2)

    def test_remove_one_missing_file(self):
        d = PathList()
        files = ["/tmp/missing.txt", "/tmp/foo.txt", "/tmp/bar.txt"]
        d.add(*files)
        self.assertEqual(len(d), 3)
        d.remove_missing()
        self.assertEqual(len(d), 2)

    def test_remove_many_missing_file(self):
        d = PathList()
        files = ["/tmp/missing.txt", "/tmp/foo.txt", "/tmp/bar.txt", "/tmp/missing2.txt", "/tmp/missing3.txt"]
        d.add(*files)
        self.assertEqual(len(d), 5)
        d.remove_missing()
        self.assertEqual(len(d), 2)

    def test_remove_when_all_files_missing(self):
        d = PathList()
        files = ["/tmp/missing.txt", "/tmp/missing2.txt", "/tmp/missing3.txt"]
        d.add(*files)
        self.assertEqual(len(d), 3)
        d.remove_missing()
        self.assertFalse(d)

    def test_remove_missing_when_dups_given(self):
        d = PathList()
        files = ["/tmp/missing", "/tmp/foo", "/tmp/bar",  "/tmp/foo", "/tmp/missing2", "/tmp/missing"]
        d.add(*files)
        self.assertEqual(len(d), 4)
        d.remove_missing()
        self.assertEqual(len(d), 2)


    def test_dont_remove_globbable_files(self):
        d = PathList()
        files = ["/tmp/foo","/tmp/missing*", "/tmp/missing.[0-9]", "/tmp/missing.????.exr"]
        d.add(*files)
        self.assertEqual(len(d), 4)
        d.remove_missing()
        self.assertEqual(len(d), 4)

if __name__ == "__main__":
    unittest.main()
