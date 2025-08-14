from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher


if __name__ == "__main__":
    filePath = r"/offlineSimStuff/variousGraphingTools/outDated/completeLogs/Sizable_inventory.json"
    completeGrapher = CompleteGrapher()
    #completeGrapher.create_graphs_with_file(filePath)
    completeGrapher.draw_long_term_graphs_given_file(filePath)