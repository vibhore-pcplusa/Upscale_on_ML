import nbformat
with open('stage5_modelling.ipynb') as f:
    nb = nbformat.read(f, as_version=4)
for cell in nb.cells:
    if cell.cell_type == 'code':
        for output in cell.outputs:
            if 'text' in output:
                print(output.text)
