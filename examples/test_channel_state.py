import tempfile
import unittest
from pathlib import Path

from channel_state import ChannelState


class ChannelStateTests(unittest.TestCase):
    def test_success_is_not_sent_twice(self):
        with tempfile.TemporaryDirectory() as folder:
            sent = []
            state = ChannelState(Path(folder) / "state.json")
            self.assertTrue(state.deliver("telegram", "hello", sent.append))
            self.assertFalse(state.deliver("telegram", "hello", sent.append))
            self.assertEqual(sent, ["hello"])

    def test_failed_chunk_resumes_without_repeating_success(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            sent = []

            def fail_on_second(chunk):
                if len(sent) == 1:
                    raise RuntimeError("temporary failure")
                sent.append(chunk)

            with self.assertRaises(RuntimeError):
                ChannelState(path).deliver("kakao", "abcdef", fail_on_second, 2)

            resumed = []
            ChannelState(path).deliver("kakao", "abcdef", resumed.append, 2)
            self.assertEqual(sent, ["ab"])
            self.assertEqual(resumed, ["cd", "ef"])

    def test_channels_have_independent_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.json"
            telegram = []
            slack = []
            state = ChannelState(path)
            state.deliver("telegram", "same", telegram.append)
            state.deliver("slack", "same", slack.append)
            self.assertEqual(telegram, ["same"])
            self.assertEqual(slack, ["same"])


if __name__ == "__main__":
    unittest.main()

