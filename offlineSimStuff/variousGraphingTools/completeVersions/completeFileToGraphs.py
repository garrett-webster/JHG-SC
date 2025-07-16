from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher


if __name__ == "__main__":
    filePath = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\variousGraphingTools\completeVersions\completeLogs\Sizable_inventory.json"
    completeGrapher = CompleteGrapher()
    #completeGrapher.create_graphs_with_file(filePath)
    completeGrapher.draw_long_term_graphs_given_file(filePath)