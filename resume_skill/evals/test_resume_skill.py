import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

import frontmatter


SKILL_DIR = Path(__file__).resolve().parents[1]


def load_script(name):
    path = SKILL_DIR / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


csv_to_md = load_script("csv_to_md")
render = load_script("render")


class CsvToMarkdownTests(unittest.TestCase):
    def test_front_matter_handles_colons_newlines_and_numeric_strings(self):
        meta = {
            "name": "张三: 后端",
            "phone": "01234567890",
            "email": "test@example.com",
        }
        md = csv_to_md.to_markdown(
            meta,
            {"期望职位": "研发: 后端"},
            "第一行\n第二行",
            [],
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.md"
            path.write_text(md, encoding="utf-8")
            post = frontmatter.load(path)

        self.assertEqual(post["name"], "张三: 后端")
        self.assertEqual(post["phone"], "01234567890")
        self.assertEqual(post["intent"], "研发: 后端")
        self.assertEqual(post["summary"], "第一行\n第二行")

    def test_legacy_xls_is_rejected_with_clear_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.xls"
            path.write_bytes(b"not-an-xlsx-file")
            with self.assertRaisesRegex(SystemExit, "不支持旧版 .xls"):
                csv_to_md.read_rows(path)

    def test_bundled_csv_example_builds_a_renderable_resume(self):
        rows = csv_to_md.read_rows(SKILL_DIR / "assets" / "resume.example.csv")
        meta, intent_parts, summary, groups = csv_to_md.build(rows)
        md = csv_to_md.to_markdown(meta, intent_parts, summary, groups)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.md"
            path.write_text(md, encoding="utf-8")
            parsed_meta, sections = render.parse_resume(path)

        render.validate_resume(parsed_meta, sections)
        self.assertEqual(parsed_meta["name"], "库森")
        self.assertGreaterEqual(len(sections), 4)

    def test_xlsx_input_is_supported(self):
        import openpyxl

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["分类", "字段名", "值"])
            sheet.append(["基本信息", "姓名", "库森"])
            workbook.save(path)

            rows = csv_to_md.read_rows(path)

        self.assertEqual(rows[1], ["基本信息", "姓名", "库森"])

    def test_xlsx_rejects_numeric_values_beyond_excel_precision(self):
        import openpyxl

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["分类", "字段名", "值"])
            sheet.append(["基本信息", "身份证号", 330100199901010000])
            workbook.save(path)

            with self.assertRaisesRegex(SystemExit, "设为“文本”"):
                csv_to_md.read_rows(path)

    def test_private_id_is_commented_out(self):
        md = csv_to_md.to_markdown(
            {"name": "库森", "id_number": "330100199901010000"},
            {},
            "",
            [],
        )

        post = frontmatter.loads(md)
        self.assertNotIn("id_number", post.metadata)
        self.assertIn("# id_number:", md)


class RenderTests(unittest.TestCase):
    def test_template_discovery_only_returns_renderable_templates(self):
        self.assertEqual(
            render.available_templates(),
            ["classic", "compact", "minimal", "modern", "timeline"],
        )

    def test_html_escapes_metadata_titles_and_headings(self):
        meta = {"name": "<测试 & 用户>", "intent": "研发 <后端>"}
        sections = [{
            "title": "项目 <经验>",
            "bullets": [],
            "entries": [{
                "title_parts": ["A & B", "<核心开发>"],
                "meta": "2024 < 2025",
                "bullets": [render.inline_md("使用 **A&B** 与 `<unsafe>`")],
            }],
        }]

        output = render.render_html(meta, sections, "classic")

        self.assertIn("&lt;测试 &amp; 用户&gt;", output)
        self.assertIn("项目 &lt;经验&gt;", output)
        self.assertIn("<strong>A &amp; B</strong>", output)
        self.assertIn("&lt;核心开发&gt;", output)
        self.assertIn("2024 &lt; 2025", output)
        self.assertIn("<strong>A&amp;B</strong>", output)
        self.assertIn("<code>&lt;unsafe&gt;</code>", output)

    def test_inline_markdown_has_valid_triple_emphasis_order(self):
        output = str(render.inline_md("***粗斜体***"))
        self.assertEqual(output, "<strong><em>粗斜体</em></strong>")

    def test_heading_accepts_ascii_or_fullwidth_separators_without_spaces(self):
        ascii_heading = render.parse_entry_heading("### 公司|2024.01-2024.06")
        fullwidth_heading = render.parse_entry_heading("### 公司·部门｜2024.01-2024.06")
        alternate_heading = render.parse_entry_heading("### 公司・部门•岗位 | 2025.01-2025.06")

        self.assertEqual(ascii_heading, {
            "title_parts": ["公司"],
            "meta": "2024.01-2024.06",
        })
        self.assertEqual(fullwidth_heading, {
            "title_parts": ["公司", "部门"],
            "meta": "2024.01-2024.06",
        })
        self.assertEqual(alternate_heading, {
            "title_parts": ["公司", "部门", "岗位"],
            "meta": "2025.01-2025.06",
        })

    def test_invalid_accent_is_rejected(self):
        with self.assertRaises(SystemExit):
            render.render_html({}, [], "modern", accent="red; } body { color: red")

    def test_orange_accent_preset_is_injected_into_template_css(self):
        self.assertEqual(render.ACCENT_PRESETS.get("orange"), "#c65d21")

        output = render.render_html({}, [], "modern", accent="orange")

        self.assertIn(":root { --accent: #c65d21; }", output)

    def test_custom_hex_accent_is_supported(self):
        output = render.render_html({}, [], "modern", accent="#1f6feb")
        self.assertIn(":root { --accent: #1f6feb; }", output)

    def test_classic_template_remains_accent_independent(self):
        classic_css = (
            SKILL_DIR / "assets" / "templates" / "classic" / "style.css"
        ).read_text(encoding="utf-8")
        compact_css = (
            SKILL_DIR / "assets" / "templates" / "compact" / "style.css"
        ).read_text(encoding="utf-8")

        self.assertNotIn("var(--accent)", classic_css)
        self.assertIn("var(--accent)", compact_css)

    def test_optional_photo_is_rendered_by_supported_templates(self):
        for template in ("classic", "compact", "modern", "minimal"):
            with self.subTest(template=template):
                output = render.render_html({"name": "库森", "photo": "avatar.png"}, [], template)
                self.assertIn('src="avatar.png"', output)

        timeline = render.render_html({"name": "库森", "photo": "avatar.png"}, [], "timeline")
        self.assertNotIn('src="avatar.png"', timeline)

    def test_intent_detail_is_rendered_by_all_templates(self):
        meta = {
            "name": "库森",
            "intent": "后端开发工程师",
            "intent_detail": "期望地点：杭州 · 到岗时间：2026.06",
        }
        for template in render.available_templates():
            with self.subTest(template=template):
                output = render.render_html(meta, [], template)
                self.assertIn("期望地点：杭州", output)

    def test_resume_requires_a_name(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit):
            render.validate_resume({}, [])
        self.assertIn("缺少必填字段 name", stderr.getvalue())

    def test_ensure_parent_creates_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "nested" / "resume.pdf"
            render.ensure_parent(output)
            self.assertTrue(output.parent.is_dir())

    def test_bundled_markdown_example_is_one_a4_page_in_all_templates(self):
        from weasyprint import HTML

        md_path = SKILL_DIR / "assets" / "resume.example.md"
        meta, sections = render.parse_resume(md_path)
        render.validate_resume(meta, sections)

        for template in render.available_templates():
            with self.subTest(template=template):
                html = render.render_html(meta, sections, template)
                document = HTML(string=html, base_url=str(md_path.parent)).render()
                self.assertEqual(len(document.pages), 1)
                self.assertAlmostEqual(document.pages[0].width, 793.7, delta=1)
                self.assertAlmostEqual(document.pages[0].height, 1122.5, delta=1)

    def test_long_resume_paginates_to_multiple_a4_pages(self):
        from weasyprint import HTML

        md_path = SKILL_DIR / "assets" / "resume.example.md"
        meta, sections = render.parse_resume(md_path)
        long_sections = sections * 3

        for template in render.available_templates():
            with self.subTest(template=template):
                html = render.render_html(meta, long_sections, template)
                document = HTML(string=html, base_url=str(md_path.parent)).render()
                self.assertGreaterEqual(len(document.pages), 2)
                for page in document.pages:
                    self.assertAlmostEqual(page.width, 793.7, delta=1)
                    self.assertAlmostEqual(page.height, 1122.5, delta=1)


if __name__ == "__main__":
    unittest.main()
