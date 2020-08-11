function showResults(results){
    for (var i = results.length - 1; i >= 0; i--) {
      var tr = $("<tr></tr>");
      tr.append($("<td>"+results[i]["title"]+"</td>"));
      tr.append($("<td><a target=\"_blank\" rel=\"noopener noreferrer\" href=\"/"+results[i]["fname"]+"\">View</a></td>"));
      tr.append($("<td><a href=\"pdfefile:///SyncedFolders/"+results[i]["fname"]+"\">Open in PDFExpert</a></td>"));
      $("#results").append(tr);
    }
}

$(window).on('load', function () {
  showResults(references);
});
