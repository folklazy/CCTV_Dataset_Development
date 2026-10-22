"""Check split boundaries and ZIP directory access using synthetic bytes only."""
import importlib.util
import sys
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

spec = importlib.util.spec_from_file_location(
    "audit_package", Path(__file__).resolve().parents[1] / "scripts/audit_package.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SplitArchiveTests(unittest.TestCase):
    def test_delivered_timestamp_preserves_explicit_offset(self):
        from datetime import timezone
        value = module.parse_timestamp("2025-01-02 15:59:59.819 +0700")
        self.assertEqual(value.astimezone(timezone.utc).isoformat(),
                         "2025-01-02T08:59:59.819000+00:00")
        with self.assertRaises(ValueError):
            module.parse_timestamp("unknown")

    def test_spreadsheet_empty_inline_cell(self):
        buffer = io.BytesIO()
        xml = '''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
        <sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>note</t></is></c></row>
        <row r="2"><c r="A2" t="inlineStr"/></row></sheetData></worksheet>'''
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("xl/worksheets/sheet1.xml", xml)
        self.assertEqual(module.spreadsheet_rows(buffer.getvalue()), (["note"], [{"note": ""}]))

    def test_seek_and_read_cross_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / str(i) for i in range(3)]
            for path, payload in zip(paths, [b"abc", b"defgh", b"ijk"]):
                path.write_bytes(payload)
            with module.SplitArchive(paths) as stream:
                self.assertEqual(stream.read(5), b"abcde")
                stream.seek(-2, io.SEEK_CUR)
                self.assertEqual(stream.read(6), b"defghi")
                stream.seek(-3, io.SEEK_END)
                self.assertEqual(stream.read(), b"ijk")
                self.assertEqual(stream.read(1), b"")
                stream.seek(20)
                self.assertEqual(stream.read(), b"")
                with self.assertRaises(ValueError):
                    stream.seek(-1)

    def test_zip_directory_across_many_parts(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("images/a.jpg", b"synthetic fixture, not CCTV")
            archive.writestr("images/b.jpg", b"second synthetic fixture")
        payload = buffer.getvalue()
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for i, start in enumerate(range(0, len(payload), 23)):
                path = Path(directory) / str(i)
                path.write_bytes(payload[start:start + 23])
                paths.append(path)
            with module.SplitArchive(paths) as stream, zipfile.ZipFile(stream) as archive:
                self.assertEqual(archive.namelist(), ["images/a.jpg", "images/b.jpg"])
                self.assertEqual(archive.infolist()[0].file_size, 27)


if __name__ == "__main__":
    unittest.main()
