import unittest
from enum_status import TaskStatus, is_finished

class TaskStatusTests(unittest.TestCase):
    def test_only_done_is_finished(self):
        self.assertFalse(is_finished(TaskStatus.TODO))
        self.assertFalse(is_finished(TaskStatus.IN_PROGRESS))
        self.assertTrue(is_finished(TaskStatus.DONE))

if __name__ == "__main__":
    unittest.main()
