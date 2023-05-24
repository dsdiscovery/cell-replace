import argparse
import nbformat
from collections.abc import Mapping

TEST_PREFIX = '### TEST CASE'

def is_test_cell(cell: dict) -> bool:
    """Checks if `cell` is a test cell."""
    if cell['cell_type'] != 'code':
        return False
    return cell['source'].startswith(TEST_PREFIX)

def get_test_cell_id(cell: dict) -> str:
    """Returns a test cell's ID.

    NOTE: This function assumes that cell is a well-formatted test cell.
    """
    first_line = cell['source'].splitlines()[0]
    test_id = first_line.split('--')[1].strip()
    return test_id

def build_id_dict(
        nb: nbformat.NotebookNode
    ) -> Mapping[str, str]:
    """Returns a dictionary from `nb` mapping test IDs to cell contents.

    For each test cell, maps the test's ID to its contents. Used for quick
    notebook lookups at cell replacement time.        
    """
    id_dict = dict()
    for cell in nb.cells:
        if is_test_cell(cell):
            id_dict[get_test_cell_id(cell)] = cell['source']
    return id_dict

def replace_autograding_cells(
        student_nb: nbformat.NotebookNode,
        reference_nb: nbformat.NotebookNode
    ) -> nbformat.NotebookNode:
    """Replaces autograding cells in `student`.

    Replaces all cells in `student` that are marked with a prefix of
    ### TEST CASE -- ID with a cell from `reference` containing the
    same ID.

    Args:
        student: The student's working notebook
        reference: The reference notebook, usually fetched from release
    
    Returns:
        A notebook with replaced test cells
    
    Raises:
        LookupError: A test cell in reference cannot be located in `student`
    """
    # check to make sure all necessary test cells exist inside student_nb
    student_test_cells = build_id_dict(student_nb)
    reference_test_cells = build_id_dict(reference_nb)
    for test_id in reference_test_cells.keys():
        if test_id not in student_test_cells:
            raise LookupError(f'A test cell with ID {test_id} could not be'
                               ' found in your MicroProject notebook. Please'
                               ' verify that you have not deleted any test'
                               ' cells in your notebook. If you have'
                               ' deleted a test cell, you may replace'
                               ' it by manually copying it from release'
                               ' or rolling your repository back to a previous'
                               ' commit (note, the latter may undo your)'
                               ' work!)')
    # replace student_nb's test cell contents with those from release
    for i in range(len(student_nb.cells)):
        if is_test_cell(student_nb.cells[i]):
            cell_id = get_test_cell_id(student_nb.cells[i])
            student_nb.cells[i]['source'] = reference_test_cells[cell_id]
    return student_nb

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('student_fp', action='store',
                        help='Filepath a the student\'s notebook.')
    parser.add_argument('reference_fp', action='store',
                        help='Filepath to the reference notebook.')
    args = parser.parse_args()
    student_nb = nbformat.read(args.student_fp, as_version=4)
    reference_nb = nbformat.read(args.reference_fp, as_version=4)
    final_nb = replace_autograding_cells(student_nb, reference_nb)
    nbformat.write(final_nb, f'{args.assignment_name}.ipynb')