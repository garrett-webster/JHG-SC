def test_randomGeneString():
    numGeneCopies = 1
    newGene1 = randomGeneString(numGeneCopies)
    newGene2 = randomGeneString(numGeneCopies)

    assert newGene2 != newGene1

def test_extractGene(): # write the edge cases as we go
    gene_dict = {} # something
    new_gene_extraction = extractGene(gene_dict)
    hardcoded_gene = [30,29,] # hardcoded gene
    assert new_gene_extraction == hardcoded_gene