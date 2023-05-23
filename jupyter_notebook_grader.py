from typing import List, Dict, Callable
from collections import defaultdict

import nbformat

class TestcellBlock:
    cases: List[str]
    blocks: Dict[str, List[str]]

    def __init__(
            self
        ):
        self.cases = []
        self.blocks = defaultdict(lambda: [])

    def add_codeblock(
            self, 
            testcase: str, 
            code: str
        ):
        block = self.blocks[testcase]
        if len(block) == 0:
            self.cases.append(testcase)

        block.append(code)

    def compile_into_py(
            self,
            cases: List[str] = [],
            transform_block: Callable[[str], str] = lambda x: x
        ) -> str:
        if len(cases) == 0:
            cases = self.cases

        py_code = ""
        for testcase in cases:
            section = "\n".join(self.blocks[testcase])
            py_code += transform_block(section)

        return py_code

def open_notebook(
        path: str    
    ) -> nbformat.NotebookNode:
    with open(path, "r") as nfp:
        notebook = nbformat.read(nfp, as_version=6)
    return notebook

def extract_with_prefix(
        notebook: nbformat.NotebookNode,
        prefix: str
    ) -> TestcellBlock:
    per_testcase_code = TestcellBlock()

    for cell in notebook.cells:
        if cell.cell_type == "code":
            source = cell.source
            first_line, rest = source.split("\n", 1)
            if first_line.startswith(prefix):
                testcase_name = first_line.split(prefix)[1].strip()
                per_testcase_code.add_codeblock(testcase_name, rest)
    
    return per_testcase_code


