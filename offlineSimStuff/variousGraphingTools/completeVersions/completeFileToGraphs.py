from offlineSimStuff.variousGraphingTools.completeVersions.completeGrapher import CompleteGrapher


if __name__ == "__main__":
    filePath = r"C:\Users\Sean\Documents\GitHub\OtherGarrettStuff\JHG-SC\offlineSimStuff\variousGraphingTools\completeVersions\completeLogs\WHEEEE.json"
    completeGrapher = CompleteGrapher()
    completeGrapher.create_graphs_with_file(filePath)